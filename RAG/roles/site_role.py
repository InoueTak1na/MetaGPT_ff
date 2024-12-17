from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from typing import Optional
from RAG.actions.site_action import SiteAction
from RAG.actions.analyze_query import AnalyzeQuery

class SiteRole(Role):
    """站址地图角色"""
    name: str = "GIS-PUBLIC-SITE"
    profile: str = "站址地图展示专家"
    goal: str = "展示和分析站址分布信息"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SiteAction])
        self._watch([AnalyzeQuery])
        
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        
        msg = self.get_memories(k=1)[0]
        result = await todo.run(msg.content)
        return Message(content=result, role=self.profile, cause_by=type(todo))
