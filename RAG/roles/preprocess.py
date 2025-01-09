from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from RAG.actions.pre_query import PreAction
from RAG.actions.iprec_action import IPAction
from RAG.actions.cityrec_action import CityAction
from typing import Optional
from metagpt.utils.common import any_to_str

class PreProcess(Role):
    """预处理角色"""
    name: str = "PRE_PROCESS"
    profile: str = "需求转换智能体"
    goal: str = "应对需求中需要转换和处理的数据"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([PreAction])
        # self._set_react_mode(react_mode="react")
        self._watch([IPAction, CityAction])
        self.addresses = {self.name, "PRE_PROCESS", "数据预处理智能体"}
        self.pending_queries = []  # 存储待处理的查询
        self.completed_queries = []  # 存储已完成的查询
        
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo 
        
        # 获取最新消息并检查是否是发给自己的
        while True:
            msg = self.get_memories(k=1)[0]
            if self.name not in msg.send_to:  # 不是发给自己的消息
                return None
            if msg.cause_by == type(todo):  # 是自己产生的消息
                return None
            break
            
        result = await todo.run(msg.content)
        return Message(
            content=result, 
            role=self.profile, 
            cause_by=type(todo),
            #send_from=self.name,
            send_to={"Center"}
        )
