import asyncio
from metagpt.actions import Action
from metagpt.environment import Environment
from openai import AsyncOpenAI
from metagpt.roles import Role
from metagpt.team import Team

action1 = Action(name="池国枫说", instruction="陈诉你的关于环境保护的观点并且不重复")
action2 = Action(name="陈博嵘说", instruction="陈诉你的关于环境保护的观点并且不重复")
chigf = Role(name="池国枫", profile="民主党候选人", goal="赢得选举", actions=[action1], watch=[action2])
cbr = Role(name="陈博嵘", profile="共和党候选人", goal="赢得选举", actions=[action2], watch=[action1])
env = Environment(desc="US选举直播")
team = Team(investment=10.0, env=env, roles=[chigf, cbr])

asyncio.run(team.run(idea="主题:气候变化，限80字", send_to="池国枫", n_round=5))
