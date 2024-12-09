from metagpt.context import Context
from WorldNews.roles.fetcher import Fetcher
from WorldNews.roles.DB_manager import DBManager
from metagpt.team import Team
import asyncio

def main():
    ctx = Context()
    company = Team(context=ctx)
    
    # 创建角色并设置关系
    fetcher = Fetcher()
    db_manager = DBManager()
    
    company.hire([db_manager, fetcher])
    
    # 设置更多轮次以确保所有新闻都能被处理
    company.run_project("创建数据库和表")
    asyncio.run(company.run(n_round=3))

if __name__ == "__main__":
    main()