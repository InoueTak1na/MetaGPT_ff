from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from RAG.actions.analyze_query import SplitQuery
from metagpt.actions.add_requirement import UserRequirement
from RAG.actions.bbu_action import BBUAction
from RAG.actions.cell_action import CellAction
from RAG.actions.map_action import MapAction
from RAG.actions.site_action import SiteAction
from typing import Optional
from metagpt.utils.common import any_to_str

class Center(Role):
    """中心调度角色,负责分析用户需求并调用对应角色"""
    
    name: str = "Center"
    profile: str = "中心调度员"
    goal: str = "分析用户需求并调用合适的角色处理"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SplitQuery])
        self._set_react_mode(react_mode="react")
        self._watch([UserRequirement, BBUAction, CellAction, MapAction, SiteAction])
        self.pending_queries = []  # 存储待处理的查询
        self.completed_queries = []  # 存储已完成的查询
    
    async def _act(self) -> Optional[Message]:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        
        msg = self.get_memories(k=1)[0]
        if msg.cause_by == type(self):
            return None
            
        # 如果是用户查询，进行拆分并开始处理
        if any_to_str(msg.cause_by) == "metagpt.actions.add_requirement.UserRequirement":
            # 分析查询并获取查询列表
            queries = await todo.run(msg.content)
            
            if not queries:
                return Message(
                    content="无法分析查询内容",
                    role=self.name
                )
            
            # 保存所有待处理的查询
            self.pending_queries = queries.copy()
            self.completed_queries = []
            
            # 发送第一个查询
            if self.pending_queries:
                query = self.pending_queries[0]
                sub_msg = Message(
                    content=query["query"],
                    role=self.name,
                    cause_by=type(todo),
                    sent_from=self.name,
                    send_to={query["role"]}
                )
                self.publish_message(sub_msg)
            
            return None
            
        # 如果是角色返回的结果，处理下一个查询
        else:
            if not self.pending_queries:  # 没有待处理的查询了
                return None
                
            # 记录已完成的查询
            completed_query = self.pending_queries.pop(0)
            self.completed_queries.append({
                "query": completed_query,
                "result": msg.content
            })
            
            # 如果还有待处理的查询，发送下一个
            if self.pending_queries:
                next_query = self.pending_queries[0]
                sub_msg = Message(
                    content=next_query["query"],
                    role=self.name,
                    cause_by=type(todo),
                    sent_from=self.name,
                    send_to={next_query["role"]}
                )
                self.publish_message(sub_msg)
            else:
                # 所有查询都完成了，返回汇总结果
                summary = "\n".join([
                    f"{item['query']['role']}: {item['result']}"
                    for item in self.completed_queries
                ])
                return Message(
                    content=summary,
                    role=self.name,
                    cause_by=type(todo)
                )
            
            return None