from metagpt.roles import Role
from WorldNews.actions.fetch_news import FetchTitle
from WorldNews.actions.DB_manage import CreateDB
from metagpt.logs import logger
from metagpt.schema import Message


class Fetcher(Role):
    name: str = "Fetcher"
    profile: str = "新闻获取者, "
    goal: str = "获取最新的国际新闻"
    constraints: str = "确保获取的新闻是最新的"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([FetchTitle])
        self._watch([CreateDB])

    async def _act(self):
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        await todo.run()
