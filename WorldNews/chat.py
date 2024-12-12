from WorldNews.roles.xiaobing import Xiaobing
import asyncio

async def main():
    msg = "HYH指的是谁"
    role = Xiaobing()
    result = await role.run(msg)
    print(result)

asyncio.run(main())