from WorldNews.roles.fetcher import Fetcher
import asyncio
from metagpt.context import Context
from metagpt.logs import logger

async def main():
    context = Context()
    fetcher = Fetcher(context=context)
    await fetcher.run("国际运营商")

if __name__ == "__main__":
    asyncio.run(main())