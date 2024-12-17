import typer
import asyncio
from metagpt.logs import logger
from metagpt.team import Team
from RAG.roles.center import Center
from RAG.roles.bbu_role import BBURole
from RAG.roles.cell_role import CellRole
from RAG.roles.map_role import MapRole
from RAG.roles.site_role import SiteRole

app = typer.Typer()

@app.command()
def main(
    query: str = typer.Option(..., help="查询内容"),
):
    async def async_main():
        logger.info(f"query: {query}")

        team = Team()
        team.hire(
            [Center(), BBURole(), CellRole(), MapRole(), SiteRole()]
        )
        team.run_project(idea=query)
        await team.run(n_round=5)

    # 调用 asyncio.run() 运行异步逻辑
    asyncio.run(async_main())

if __name__ == "__main__":
    app()
