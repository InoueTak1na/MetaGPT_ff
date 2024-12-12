import asyncio
from pydantic import BaseModel
from metagpt.rag.engines import SimpleEngine
from metagpt.rag.interface import RAGObject
from llama_index.embeddings.dashscope import DashScopeEmbedding

def get_embedding(model_name: str = "text-embedding-v3"):
    return DashScopeEmbedding(
        model_name=model_name,
        api_key="sk-3437f4165f7e4c2b96fd8df81db8e929",
        embed_batch_size=6
    )

class Player(BaseModel):
    name: str
    goal: str
    
    def rag_key(self) -> str:
        return f"{self.name}'s goal is {self.goal}"

async def main():
    objs = [Player(name="Jeff", goal="Top One"), Player(name="Mike", goal="Top Three")]
    engine = SimpleEngine.from_objs(objs=objs, embed_model=get_embedding())
    answer = await engine.aquery("What is Jeff's goal?")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())