from metagpt.roles import Role
from ffai.actions.crawl import Crawl, GenerateSelectors, ExtractData
from metagpt.schema import Message
from metagpt.logs import logger
import json

class WebCrawler(Role):
    name: str = "WebCrawler"
    profile: str = "Web Crawler Engineer"
    goal: str = "高效地爬取网页内容并提取所需数据"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([Crawl, GenerateSelectors, ExtractData])
        self._set_react_mode(react_mode="by_order")
    
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        
        if isinstance(todo, Crawl):
            args = json.loads(msg.content)
            result = await todo.run(url=args['url'])
        elif isinstance(todo, GenerateSelectors):
            args = json.loads(self.get_memories(k=2)[0].content)
            result = await todo.run(
                content=msg.content,
                requirement=args['requirement']
            )
            result = json.dumps(result, ensure_ascii=False)
        elif isinstance(todo, ExtractData):
            html_content = self.get_memories(k=2)[0].content
            selectors = json.loads(msg.content)
            result = await todo.run(html_content, selectors)
        else:
            logger.warning(f"未知的任务类型: {type(todo)}")
            return Message(content="未知的任务类型", role=self.profile)

        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self.rc.memory.add(msg)
        return msg
