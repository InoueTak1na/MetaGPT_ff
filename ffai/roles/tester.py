from metagpt.roles import Role
from ffai.actions.simple_write_test import SimpleWriteTest, SimpleRunTest
from ffai.actions.simple_write_code import SimpleWriteCode
from metagpt.schema import Message
from metagpt.logs import logger

class SimpleTester(Role):
    name: str = "Bob"
    profile: str = "SimpleTester"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteTest, SimpleRunTest])
        self._set_react_mode(react_mode="by_order")
        self._watch([SimpleWriteCode])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        msg = self.get_memories(k=1)[0] # 获得最新的k条记忆
        result = await todo.run(msg.content)
        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(msg) 
    
        return msg