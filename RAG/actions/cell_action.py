from metagpt.actions import Action
from metagpt.logs import logger

class CellAction(Action):
    """处理小区相关的查询"""
    name: str = "CellAction"

    async def run(self, query: str) -> str:
        try:
            # 这里添加实际的小区查询逻辑
            logger.info("成功调用CELL")
            return f"小区查询结果: {query}"
        except Exception as e:
            logger.error(f"小区查询失败: {str(e)}")
            return "小区查询出错" 