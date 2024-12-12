from metagpt.actions.action import Action
from metagpt.rag.engines import SimpleEngine
from pathlib import Path


class Chat(Action):
    name: str = "chat"
    PROMPT_TEMPLATE: str = """
    你是一个聊天机器人。请基于以下相关文档内容来回答用户的问题:
    
    相关文档内容: {context}
    
    用户问题: {question}
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化RAG引擎
        docs_path = Path("/Users/yanglinchen/Documents/中电福富/MetaGPT/WorldNews/Documents/knowledge.json")
        self.engine = SimpleEngine.from_docs(
            input_files=[docs_path],
            # 可选: 添加重排序提高相关性
            # ranker_configs=[LLMRankerConfig()]
        )

    async def run(self, msg: str):
        # 使用RAG检索相关内容
        nodes = await self.engine.aretrieve(msg)
        context = "\n".join([node.text for node in nodes])
        
        # 构建带上下文的提示
        prompt = self.PROMPT_TEMPLATE.format(
            context=context,
            question=msg
        )
        
        rsp = await self._aask(prompt)
        return rsp
