import typer
import asyncio
from metagpt.logs import logger
from metagpt.team import Team
from ffai.roles.programmer import SimpleCoder, RunnableCoder
from ffai.roles.tester import SimpleTester
from ffai.roles.reviewer import SimpleReviewer

app = typer.Typer()

@app.command()
def main(
    idea: str = typer.Option(..., help="write a function that calculates the product of a list"),
    investment: float = typer.Option(3.0, help="Dollar amount to invest in the AI company."),
    n_round: int = typer.Option(5, help="Number of rounds for the simulation."),
    add_human: bool = False,
):
    async def async_main():
        logger.info(f"idea: {idea}, investment: {investment}, n_round: {n_round}, add_human: {add_human}")

        team = Team()
        team.hire(
            [
                SimpleCoder(),
                SimpleTester(),
                SimpleReviewer(),
            ]
        )
        team.invest(investment=investment)
        team.run_project(idea=idea)
        await team.run(n_round=n_round)

    # 调用 asyncio.run() 运行异步逻辑
    asyncio.run(async_main())

if __name__ == "__main__":
    app()
