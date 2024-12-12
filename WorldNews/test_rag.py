import asyncio

from metagpt.rag.engines import SimpleEngine
from metagpt.const import EXAMPLE_DATA_PATH
from metagpt.rag.schema import FAISSRetrieverConfig


DOC_PATH = EXAMPLE_DATA_PATH / "rag/demo1.txt"

async def main():
    engine = SimpleEngine.from_docs(input_files=[DOC_PATH], retriever_configs=FAISSRetrieverConfig())
    answer = await engine.aquery("如何量化植被从草地或短作物向树木的转变对流量曲线（FDC）的影响？")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())