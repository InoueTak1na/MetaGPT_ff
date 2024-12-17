from metagpt.actions import Action
from metagpt.logs import logger

class MapAction(Action):
    """处理地图相关的查询"""
    name: str = "MapAction"

    async def run(self, query: str) -> str:
        try:
            # 这里添加实际的地图查询逻辑
            logger.info("成功调用MAP")
            return f"地图查询结果: {query}"
        except Exception as e:
            logger.error(f"地图查询失败: {str(e)}")
            return "地图查询出错" 