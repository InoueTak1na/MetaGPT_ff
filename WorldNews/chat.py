from WorldNews.roles.xiaobing import Xiaobing
import asyncio

async def main():
    msg = "当汇聚单板发生LOS告警时，下游的ODUk检测点会如何响应？"
    role = Xiaobing()
    result = await role.run(msg)
    print(result)

asyncio.run(main())