from typing import Optional
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.rag.engines import SimpleEngine
from metagpt.const import EXAMPLE_DATA_PATH
from metagpt.logs import logger

class AnalyzeQuery(Action):
    """分析用户查询并决定调用哪个角色处理"""
    
    name: str = "AnalyzeQuery"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_path = EXAMPLE_DATA_PATH / "rag/场景编码.txt"
        self._engine: Optional[SimpleEngine] = None
        self._init_engine()
    
    def _init_engine(self):
        """初始化RAG引擎"""
        try:
            self._engine = SimpleEngine.from_docs(input_files=[self.doc_path])
        except Exception as e:
            logger.error(f"初始化RAG引擎失败: {str(e)}")
            self._engine = None
    
    async def _get_context(self, query: str) -> Optional[str]:
        """使用RAG获取相关知识"""
        try:
            if not self._engine:
                self._init_engine()
                
            if not self._engine:
                logger.error("RAG引擎未初始化")
                return None
                
            return await self._engine.aquery(query)
        except Exception as e:
            logger.error(f"获取知识库内容时发生错误: {str(e)}")
            return None
    
    async def run(self, query: str) -> Optional[str]:
        """分析用户查询并返回合适的角色名称"""
        try:
            # 获取相关知识
            context = await self._get_context(query)
            if not context:
                return None
                
            # 根据上下文决定要调用的角色
            prompt = f"""
            基于以下信息,决定调用哪个角色处理用户需求:
            
            用户需求: {query}
            相关知识: {context}
            
            可用角色:
            1. GIS-PUBLIC-BBU - 基站地图
            2. GIS-PUBLIC-SITE - 站址地图
            3. GIS-PUBLIC-CELL - 小区地图
            4. GIS-PUBLIC-MAP - 地图
            
            请返回最合适的一个角色名称,仅返回角色名,不要其他内容
            """
            
            role_name = await self._aask(prompt)
            logger.info(f"决定调用角色: {role_name}")
            return role_name
            
        except Exception as e:
            logger.error(f"分析查询时发生错误: {str(e)}")
            return None 