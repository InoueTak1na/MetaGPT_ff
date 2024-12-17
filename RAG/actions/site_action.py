from metagpt.actions import Action
from metagpt.logs import logger

class SiteAction(Action):
    """处理站址相关的查询"""
    name: str = "SiteAction"

    async def run(self, query: str) -> str:
        try:
            # 这里添加实际的站址查询逻辑
            logger.info("成功调用SITE")
            return f"站址查询结果: {query}"
        except Exception as e:
            logger.error(f"站址查询失败: {str(e)}")
            return "站址查询出错" 