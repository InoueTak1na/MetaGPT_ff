from metagpt.roles import Role
from ffai.actions.simple_write_test import SimpleWriteTest
from ffai.actions.simple_write_code import SimpleWriteCode
from metagpt.schema import Message
from metagpt.logs import logger

class SimpleTester(Role):
    name: str = "Bob"
    profile: str = "SimpleTester"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteTest])
        self._watch([SimpleWriteCode])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        context = self.get_memories() # 获取所有的记忆

        code_text = await todo.run(context, k=5)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))

        return msg