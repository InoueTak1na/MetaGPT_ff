from metagpt.actions.action import Action


class Chat(Action):
    name: str = "QQ小冰"
    PROMPT_TEMPLATE: str = """
    你是一个聊天机器人，你叫QQ小冰，你非常擅长聊天，你非常擅长回答问题，你非常擅长解决各种问题。
    """

    async def run(self):
        prompt = self.PROMPT_TEMPLATE
        rsp = await self._aask(prompt)
        return rsp