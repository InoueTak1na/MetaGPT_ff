from metagpt.actions import Action
from metagpt.roles.role import Role, RoleReactMode
from ffai.actions.tutorial_assistant import WriteDirectory, WriteContent
from metagpt.logs import logger
from metagpt.schema import Message
from typing import Dict
import asyncio
from datetime import datetime
from metagpt.const import TUTORIAL_PATH
from metagpt.utils.file import File

class TutorialAssistant(Role):
    """
    教程助手，输入一句话即可生成标记格式的教程文档。
    参数:
        name: 角色的名称
        profile: 角色的描述
        goal: 角色的目标
        constraints: 角色的约束条件
        language: 教程文档使用的语言
    """
    name: str = "黄雨豪"
    profile: str = "教程助手"
    goal: str = "生成教程文档。"
    constraints: str = "严格遵循Markdown语法，布局整洁规范"
    language: str = "Chinese"

    topic: str = ""
    main_title: str = ""
    total_content: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteDirectory(language=self.language)])
        self._set_react_mode(react_mode=RoleReactMode.REACT.value)
    
    async def run(self, message=None):
        """观察，并根据观察结果进行思考和行动。"""
        if message:
            # 将message转换为Message对象并添加到role的记忆中
            if isinstance(message, str):
                message = Message(message)
            if isinstance(message, Message):
                self.recv(message)
            elif isinstance(message, list):
                self.recv(Message("\n".join(message)))
        elif not await self._observe():
            logger.debug(f"{self._setting}: 没有新消息，等待.")
            return
        rsp = await self.react()
        # 将回复发布到环境中，等待下一个订阅者处理
        self.publish_message(rsp)
        return rsp

    def recv(self, message: Message) -> None:
        """将消息添加到角色的记忆中。"""
        if message in self.rc.memory.get():
            return
        self.rc.memory.add(message)

    async def _think(self) -> None:
        """决定下一步角色要做的行动"""
        logger.info(self.rc.state)
        logger.info(self,)
        if self.rc.todo is None:
            self._set_state(0)
            return
        if self.rc.state + 1 < len(self.states):
            self._set_state(self.rc.state + 1)
        else:
            self.rc.todo = None
    
    async def _handle_directory(self, titles: Dict) -> Message:
        """
        处理教程文档的目录
        参数:
            titles: 教程文档的目录，例如{"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}
        返回:
            包含目录相关信息的Message对象
        """
        self.main_title = titles.get("title")
        directory = f"{self.main_title}\n"
        self.total_content += f"# {self.main_title}"
        actions = list()
        for first_dir in titles.get("directory"):
            actions.append(WriteContent(language=self.language, directory=first_dir))
            key = list(first_dir.keys())[0]
            for second_dir in first_dir.get(key):
                directory += f" - {second_dir}\n"
        self.set_actions(actions)
        self.rc.todo = None
        return Message(content=directory)
    
    async def _act(self) -> Message:
        """
        根据角色的状态执行相应的行动
        返回:
            包含行动结果的Message对象
        """
        todo = self.rc.todo
        if type(todo) is WriteDirectory:
            msg = self.rc.memory.get(k=1)[0]
            self.topic = msg.content
            resp = await todo.run(topic=self.topic)
            logger.info(resp)
            return await self._handle_directory(resp)
        resp = await todo.run(topic=self.topic)
        logger.info(resp)
        if self.total_content != "":
            self.total_content += "\n\n\n"
        self.total_content += resp
        return Message(content=resp, role=self.profile)

    async def _react(self) -> Message:
        """
        执行该助手的思考和行为
        返回:
            包含该助手最终结果的Message对象
        """
        while True:
            await self._think()
            if self.rc.todo is None:
                break
            msg = await self._act()
            root_path = TUTORIAL_PATH / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            await File.write(root_path, f"{self.main_title}.md", self.total_content.encode("utf-8"))
        return msg

