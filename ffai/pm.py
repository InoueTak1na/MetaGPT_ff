import asyncio
from metagpt.context import Context
# from ffai.roles.ProjectManager  import ProjectManager
from metagpt.roles.project_manager import ProjectManager
from metagpt.roles.architect import Architect
from metagpt.roles.product_manager import ProductManager
from metagpt.logs import logger

async def main():
    msg = "Write a cli 2048 game"
    context = Context()
    role = ProductManager(context=context)
    logger.info(msg)
    result = await role.run(msg)
    logger.info(result)

asyncio.run(main())