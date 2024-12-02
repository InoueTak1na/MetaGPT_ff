from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from ffai.actions.analyze_and_assign_tasks import AnalyzeAndAssignTasks

class ProjectManager(Role):
    name: str = "ProjectManager"
    profile: str = "Responsible for analyzing project requirements and assigning tasks"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeAndAssignTasks])
    
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        msg = self.get_memories(k=1)[0]
        result = await todo.run(msg.content)
        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(msg)
    
        return msg