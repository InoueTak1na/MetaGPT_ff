import asyncio
from metagpt.context import Context
from ffai.roles.programmer import SimpleCoder, RunnableCoder
from metagpt.logs import logger

async def main():
    msg = "Write a function that calculates the sum of a list"
    context = Context()
    role = RunnableCoder(context=context)
    logger.info(msg)
    result = await role.run(msg)
    logger.info(result)

asyncio.run(main())