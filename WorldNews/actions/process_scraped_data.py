from metagpt.actions.action import Action
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.tools.web_browser_engine_playwright import PlaywrightWrapper

class ProcessScrapedData(Action):
    name: str = "ProcessScrapedData"
    PROMPT_TEMPLATE: str = """
    Context: {context}
    分析这条国际运营商事件新闻的标题和内容，判断其情感倾向属于以下哪种类型，仅返回最后的类型，不要返回任何其他的内容：
    正面
    负面
    中性
    """

    async def run(self) -> Message:
        new_f = open('WorldNews/data/news_category.txt', 'a')
        with open('WorldNews/data/news.txt', 'r') as f:
            for line in f:
                category, title, content, url = line.split(' | ')

                prompt = self.PROMPT_TEMPLATE.format(context=f"title: {title}\ncontent: {content}")
                rsp = await self._aask(prompt)
                
                if "无关" in rsp:
                    continue
                    
                new_f.write(f"{rsp} | {title} | {content} | {url}\n")
                