from metagpt.roles import Role
from ffai.actions.simple_write_code import SimpleWriteCode
from metagpt.actions import UserRequirement
from metagpt.schema import Message
from metagpt.logs import logger
from ffai.actions.simple_wirte_review import SimpleWriteReview

class SimpleCoder(Role):
    name: str = "Alice"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteCode])
        # self._watch([SimpleWriteReview, UserRequirement])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        msg = self.get_memories(k=1)[0]
        code_text = await todo.run(msg.content)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo)) 
    
        return msg

    