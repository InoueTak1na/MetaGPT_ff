import asyncio
from metagpt.tools.web_browser_engine_playwright import PlaywrightWrapper
from bs4 import BeautifulSoup

async def main():
    wrapper = PlaywrightWrapper(browser_type="chromium", proxy="http://127.0.0.1:7890")
    page = await wrapper.run("https://www.weather.com.cn/alarm/")
    
    # 解析 HTML
    soup = BeautifulSoup(page.html, 'lxml')
    with open("logs/weather.html", "w") as f:
        f.write(str(soup))
    

asyncio.run(main())
