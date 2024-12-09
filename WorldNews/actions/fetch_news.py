from metagpt.actions.action import Action
from metagpt.tools.web_browser_engine_playwright import PlaywrightWrapper
from playwright.async_api import async_playwright
from metagpt.schema import Message
from typing import ClassVar, List, Dict


class FetchTitle(Action):
    name: str = "FetchTitle"
    PROMPT_TEMPLATE: str = """
    Context: {context}
    分析这条新闻的标题和内容，判断其是否与国际运营商相关，仅返回相关或无关，不要返回任何其他的内容：
    相关
    无关
    """
    results: ClassVar[List[Dict[str, str]]] = list()

    async def get_news_content(self, page):
        results = await page.query_selector_all("h3.t a")
        for result in results:
            title = await result.inner_text()
            content = await result.inner_html()
            url = await result.get_attribute("href")
            print(f"{title}")
            prompt = self.PROMPT_TEMPLATE.format(context=f"title: {title}\ncontent: {content}")
            rsp = await self._aask(prompt)
                
            if "无关" in rsp:
                continue
            self.results.append({"title": title, "url": url})
    async def run(self, keyword: str = "国际运营商") -> list:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await page.goto("https://www.baidu.com/s?wd=国际运营商事件")
            await page.wait_for_timeout(2000)
            await page.click('div.tool_3HMbZ.pointer_32dlN.c_font_2AD7M.hovering_1RCgm')
            await page.wait_for_timeout(1000)
            await page.wait_for_selector('#timeRlt')
            await page.click('#timeRlt')
            await page.wait_for_timeout(1000)
            await page.wait_for_selector('div.pop_over_ppVmY')
            await page.click('li.time_li_3_ArK:nth-child(2)')
            
            await page.wait_for_selector("div.result")
            await self.get_news_content(page)
            await page.click('a.n')
            
            while True:
                try:
                    await page.wait_for_timeout(2000)
                    await self.get_news_content(page)
                    
                    next_button = page.get_by_text("下一页 >")
                    if await next_button.count() > 0:  # 检查元素是否存在
                        await next_button.click()
                    else:
                        print("没有找到下一页按钮")
                        break

                except Exception as e:
                    print("已到最后一页或发生错误:", e)
                    break

            await browser.close()
            msg = Message(content=self.results,
                          role="Fetcher",
                          cause_by=type(self),
                          send_to="DBManager")
            self.rc.memory.add(msg)
            return msg

class FetchContent(Action):
    name: str = "FetchContent"
    PROMPT_TEMPLATE: str = """
    html_content: {html_content}
    提取html_content中的新闻标题、时间、来源、正文，返回一个如下json格式，不要返回任何其他的内容
    {{
        "title": "新闻标题",
        "time": "新闻时间",
        "source": "新闻来源",
        "content": "新闻正文"
    }}
    """

    async def run(self, url: str) -> str:
        wrapper = PlaywrightWrapper(browser_type="chromium")
        page = await wrapper.run(url)
        html_content = page.html
        prompt = self.PROMPT_TEMPLATE.format(html_content=html_content)
        rsp = await self._aask(prompt)
        return rsp
