from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from RAG.actions.analyze_query import AnalyzeQuery
from metagpt.actions import UserRequirement

class Center(Role):
    """中心调度角色,负责分析用户需求并调用对应角色"""
    
    name: str = "Center"
    profile: str = "中心调度员"
    goal: str = "分析用户需求并调用合适的角色处理"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeQuery])
        self._watch([UserRequirement])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        
        msg = self.get_memories(k=1)[0]
        if msg.cause_by == type(self):
            return None
            
        role_name = await todo.run(msg.content)
        
        if not role_name:
            return Message(
                content="无法确定合适的处理角色",
                role=self.name
            )
            
        return Message(
            content=msg.content,
            role=self.name,
            cause_by=type(todo),
            sent_from=self.name,
            send_to=role_name
        )