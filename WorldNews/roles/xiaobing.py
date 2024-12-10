from metagpt.roles.role import Role
from WorldNews.actions.chat import Chat
from metagpt.schema import Message
from metagpt.logs import logger

class Xiaobing(Role):
    name: str = "xiaobing"
    profile: str = "聊天机器人"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([Chat])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        rsp = await todo.run(msg.content)
        msg = Message(content=rsp, role=self.profile, cause_by=type(todo))
        return msg
