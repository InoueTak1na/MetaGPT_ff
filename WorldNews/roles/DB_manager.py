from metagpt.roles import Role
from WorldNews.actions.DB_manage import CreateDB, InsertNews, QueryNews, UpdateNewsAnalysis, UpdateNewsContent, GetUnprocessedUrls
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.actions import UserRequirement
from WorldNews.actions.fetch_news import FetchTitle

class DBManager(Role):
    name: str = "DBManager"
    profile: str = "数据库管理员"
    goal: str = "管理数据库"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreateDB, InsertNews, QueryNews, UpdateNewsAnalysis, UpdateNewsContent, GetUnprocessedUrls])
        self._set_react_mode(react_mode="react")
        self._watch([UserRequirement, FetchTitle])

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
        self.publish_message(rsp)
        return rsp

    def recv(self, message: Message) -> None:
        """将消息添加到角色的记忆中。"""
        if message in self.rc.memory.get():
            return
        self.rc.memory.add(message)
    
    async def _observe(self, ignore_memory=False) -> int:
        """观察消息队列中的新消息"""
        # 从消息缓冲区读取未处理的消息
        news = []
        if self.recovered and self.latest_observed_msg:
            news = self.rc.memory.find_news(observed=[self.latest_observed_msg], k=10)
        if not news:
            news = self.rc.msg_buffer.pop_all()
        
        # 将读取的消息存储到自己的记忆中以防止重复处理
        old_messages = [] if ignore_memory else self.rc.memory.get()
        self.rc.memory.add_batch(news)
        
        # 过滤感兴趣的消息
        self.rc.news = [
            n for n in news 
            if (n.cause_by in self.rc.watch or self.name in n.send_to)
            and n not in old_messages
        ]
        self.latest_observed_msg = self.rc.news[-1] if self.rc.news else None

        if self.rc.news:
            logger.debug(f"{self._setting} 观察到: {[f'{i.role}: {i.content[:20]}...' for i in self.rc.news]}")
        return len(self.rc.news)

    async def _think(self) -> bool:
        """根据最新消息决定下一步行动"""
        if not self.rc.news:
            return False
        
        THINK_PROMPT = """
        context: {context}
        actions: {actions}
        通过分析context，决定使用哪个action，返回action的索引号，返回结果仅包含一个数字
        """
        
        latest_msg = self.rc.news[-1]
        content = latest_msg.content
        actions = [action.name for action in self.actions]
        prompt = THINK_PROMPT.format(context=content, actions=actions)
        rsp = await self.llm.aask(prompt)
        self._set_state(int(rsp))
        
        logger.info(f"DBManager决定执行: {self.actions[self.rc.state]}")
        return True

    async def _act(self):
        """
        根据角色的状态执行相应的行为
        返回:
            包含行为结果的Message对象
        """
        todo = self.rc.todo
        if isinstance(todo, CreateDB):
            rsp = await todo.run()
            return rsp
        elif isinstance(todo, InsertNews):
            msg = self.rc.memory.get(k=1)[0]
            rsp = await todo.run()
            return rsp
        
        
    
    
