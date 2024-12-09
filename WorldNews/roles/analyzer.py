from metagpt.roles import Role
from WorldNews.actions.process_scraped_data import ProcessScrapedData
from metagpt.logs import logger
from metagpt.schema import Message

class Analyzer(Role):
    name: str = "Analyzer"
    profile: str = "新闻分析者"
    goal: str = "对获取的新闻进行情感分析"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ProcessScrapedData])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        # 传入最新的新闻消息
        return await todo.run(self.rc.news[-1] if self.rc.news else None)