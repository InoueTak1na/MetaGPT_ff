from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from RAG.actions.cityrec_action import CityAction

class CityRole(Role):
    """行政区号转换角色"""
    name: str = "CITY-RECONIZATION"
    profile: str = "行政区号转换智能体"
    goal: str = "将需求中的行政区号转换为城市名称"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CityAction])
        self.addresses = {self.name, "CITY-RECONIZATION", "行政区号转换智能体"}
        
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
                send_to="PRE_PROCESS"
                )
