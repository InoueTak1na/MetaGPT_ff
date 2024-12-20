from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from typing import Optional
from RAG.actions.bbu_action import BBUAction

class BBURole(Role):
    """基站地图角色"""
    name: str = "GIS-PUBLIC-BBU"
    profile: str = "基站地图展示专家"
    goal: str = "展示和分析基站分布信息"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([BBUAction])
        self.addresses = {self.name, "GIS-PUBLIC-BBU", "基站地图展示专家"}
        
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
        return Message(content=result, role=self.profile, cause_by=type(todo))
