from typing import Optional
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.rag.engines import SimpleEngine
from metagpt.const import EXAMPLE_DATA_PATH
from metagpt.logs import logger
from metagpt.config2 import config
from typing import List
import pdb
import re

class SplitQuery(Action):
    """分析并按需拆分用户查询"""
    name: str = "SplitQuery"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_path = EXAMPLE_DATA_PATH / "rag/场景编码.txt"
        self._engine: Optional[SimpleEngine] = None
        self._init_engine()
    def _init_engine(self):
        """初始化RAG引擎"""
        # pdb.set_trace()
        try:
            self._engine = SimpleEngine.from_docs(input_files=[self.doc_path])
            logger.info(f"RAG引擎初始化成功")
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
        

    async def run(self, query: str) -> list[dict]:
        """分析用户查询,返回查询列表(可能是单个查询或多个子查询)"""
        try:
            # 获取相关知识
            context = await self._get_context(query)

            # 暂定的划分策略
            header, squery = query.split('\n', 1)
            logger.info(f"header: {header}")
            logger.info(f"query: {squery}")

            # 将用户信息添加到context中
            context = f"{header}\n{context}" if context else header

            prompt = f"""
            分析以下用户查询,判断是否需要拆分成多个子查询。如果需要拆分,则拆分成多个独立的子查询。
            
            用户查询: {squery}
            相关知识: {context if context else "无相关知识"}
            
            可用角色:
            1. GIS-PUBLIC-BBU
            2. GIS-PUBLIC-SITE
            3. GIS-PUBLIC-CELL
            4. GIS-PUBLIC-MAP
            
            请返回Python列表格式,每个元素是一个字典,包含query和role两个键。
            如果查询不需要拆分,则返回单个元素的列表。
            如果需要拆分,则返回多个元素的列表。
            仅返回查询列表,不要其他内容。 
            请严格遵守规则,只能从可用角色中选择角色,不允许返回空白角色。

            示例输出格式:
            # 不需要拆分的情况:
            [
                {{"query": "原始查询内容", "role": "GIS-PUBLIC-BBU"}}
            ]
            
            # 需要拆分的情况:
            [
                {{"query": "子查询1", "role": "GIS-PUBLIC-BBU"}},
                {{"query": "子查询2", "role": "GIS-PUBLIC-CELL"}},
            ]
            """
            
            result = await self._aask(prompt)
            queries = eval(result)
            logger.info(f"查询分析结果: {queries}")
            return queries
            
        except Exception as e:
            logger.error(f"分析查询时发生错误: {str(e)}")
            return []