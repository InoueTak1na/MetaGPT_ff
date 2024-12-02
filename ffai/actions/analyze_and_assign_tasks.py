from metagpt.actions.action import Action
import re
from metagpt.logs import logger

class AnalyzeAndAssignTasks(Action):
    PROMPT_TEMPLATE: str = """
    Analyze the project requirements and break down the tasks into smaller, manageable units by role.
    Each task should be a single sentence.
    
    Project requirement:
    {requirement}
    Roles:
    {roles}
    """

    name: str = "AnalyzeAndAssignTasks"
    async def run(self, requirement: str):
        roles = ["Developer", "Tester", "Designer", "Project Manager"]
        prompt = self.PROMPT_TEMPLATE.format(requirement=requirement, roles="\n".join(roles))
        logger.info(prompt)
        rsp = await self._aask(prompt)
        tasks = AnalyzeAndAssignTasks.parse_tasks(rsp)
        return tasks
    
    @staticmethod
    def parse_tasks(rsp):
        tasks = rsp.split("\n")
        tasks = [task.strip() for task in tasks if task]
        return tasks
