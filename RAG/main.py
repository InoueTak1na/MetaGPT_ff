import typer
import pdb
import asyncio
from metagpt.logs import logger
from metagpt.team import Team
from RAG.roles.center import Center
from RAG.roles.bbu_role import BBURole
from RAG.roles.cell_role import CellRole
from RAG.roles.map_role import MapRole
from RAG.roles.site_role import SiteRole
from RAG.roles.iprec_role import IPRole
from RAG.roles.cityrec_role import CityRole
from RAG.roles.preprocess import PreProcess

app = typer.Typer()

@app.command()
def main(
    header: str = typer.Option(..., help="报头用户信息"),
    query: str = typer.Option(..., help="查询内容"),
):
    async def async_main():
        merged_query = f"{header}\n{query}" # 暂用换行区分报头和查询内容
        # pdb.set_trace()
        team = Team()
        team.hire(
            [Center(), BBURole(), CellRole(), MapRole(), SiteRole(), PreProcess()]
        )
        team.run_project(idea=merged_query, send_to="Center")
        await team.run(n_round=5, send_to="Center")

    # 调用 asyncio.run() 运行异步逻辑
    asyncio.run(async_main())

if __name__ == "__main__":
    app()
