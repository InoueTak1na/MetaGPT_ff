from metagpt.actions import Action
from metagpt.logs import logger
from typing import Optional
from metagpt.schema import Message
from metagpt.rag.engines import SimpleEngine
from metagpt.const import EXAMPLE_DATA_PATH
from metagpt.config2 import config
from metagpt.configs.embedding_config import EmbeddingType
from typing import List
import pdb

class PreAction(Action):
    """预处理需求"""
    name: str = "PreAction"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_path = EXAMPLE_DATA_PATH / "rag/需求转换.txt"
        self._engine: Optional[SimpleEngine] = None
        self._init_engine()
    def _init_engine(self):
        """初始化RAG引擎"""
        # pdb.set_trace()
        try:
            self._engine = SimpleEngine.from_docs(input_files=[self.doc_path])
            logger.info(f"需求转换RAG初始化成功")
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
        """分析用户查询,查看是否需要转换"""
        try:
            # 获取相关知识
            context = await self._get_context(query)
            
            prompt = f"""
            分析以下用户查询,判断是否有需要转换的数据，如果有，则提取出来，并根据知识库进行转换。
            
            用户查询: {query}
            相关知识: {context if context else "无相关知识"}
            
            请返回和原本的query相同的格式。
            如果查询不需要转换，则不做修改直接返回。
            如果需要转换，则返回转换后的查询。
            仅修改需要转换的部分，不要修改其他内容。
            仅返回修改后的查询,不要其他内容。   

            示例输出:
            query: "请查询0591 IP192.168.1.1的基站地图"
            return query: "请查询福州 东街口的基站地图"

            query: "请查询0755的小区地图,IP192.168.1.4“
            return query: "请查询深圳的小区地图,设备名龙华"
            """
            result = await self._aask(prompt)
            logger.info(f"查询转换结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"转换查询时发生错误: {str(e)}")
            return []