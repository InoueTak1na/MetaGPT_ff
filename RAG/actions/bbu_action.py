from metagpt.actions import Action
from metagpt.logs import logger

class BBUAction(Action):
    """处理BBU相关的查询"""
    name: str = "BBUAction"

    async def run(self, query: str) -> str:
        try:
            # 这里添加实际的BBU查询逻辑
            logger.info("成功调用BBU")
            return f"BBU查询结果: {query}"
        except Exception as e:
            logger.error(f"BBU查询失败: {str(e)}")
            return "BBU查询出错" 