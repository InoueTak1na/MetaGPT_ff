from typing import Optional
from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.rag.engines import SimpleEngine
from metagpt.const import EXAMPLE_DATA_PATH

class IPAction(Action):
    """处理ip转换"""
    name: str = "IPAction"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_path = EXAMPLE_DATA_PATH / "rag/IP转换.txt"
        self._engine: Optional[SimpleEngine] = None
        self._init_engine()
    def _init_engine(self):
        """初始化RAG引擎"""
        # pdb.set_trace()
        try:
            self._engine = SimpleEngine.from_docs(input_files=[self.doc_path])
            logger.info(f"IP-RAG初始化成功")
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
            prompt = f"""
                你是一个IP转换专家,你的任务是将用户的IP地址转换为设备名称.
                请注意,只需要将用户输入中的IP地址替换为设备名称,不要改变其它内容.
                然后将回答返回给用户,不要添加任何多余的内容.
                示例:
                用户输入: 你好,我是123.123.123.123
                回答: 你好,我是设备M
                用户输入: 请查询IP192.168.111.112的基站地图
                回答: 请查询设备T的基站地图
                用户输入: 请查询IP111.111.111.112的小区地图和IP22.33.44.55的基站地图
                回答: 请查询设备T的小区地图和设备Q的基站地图
                用户输入: {query}
                """
    
            return await self._engine.aquery(prompt)
        except Exception as e:
            logger.error(f"获取知识库内容时发生错误: {str(e)}")
            return None
        
    async def run(self, query: str) -> str:
        try:
            # 获取相关知识
            context = await self._get_context(query)
            print(context)
            return f"IP查询结果: {context}"
        except Exception as e:
            logger.error(f"IP查询失败: {str(e)}")
            return "IP查询出错" 