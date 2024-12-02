from ffai.roles.crawler import WebCrawler
import asyncio
from metagpt.context import Context
from metagpt.logs import logger
import json
async def main():
    context = Context()
    crawler = WebCrawler(context=context)
    # 直接传入包含url和requirement的字典
    args = {
        'url': 'https://www.weather.com.cn/alarm/',
        'requirement': '预警信息'
    }
    
    logger.info(f"开始爬取: {args['url']}")
    result = await crawler.run(json.dumps(args))
    logger.info(f"提取到的数据: {result}")

if __name__ == "__main__":
    asyncio.run(main())