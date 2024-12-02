from ffai.roles.Assistant import TutorialAssistant
from metagpt.logs import logger
import asyncio

async def main():
    msg = "HTML 的基本结构、标签和常见元素"
    role = TutorialAssistant()
    logger.info(msg)
    result = await role.run(msg)
    logger.info(result)

if __name__ == "__main__":
    asyncio.run(main())