from metagpt.actions import Action

class Chat(Action):
    def __init__(self, context=None, name="Chat"):
        super().__init__(name=name, context=context)
    
    async def run(self, *args, **kwargs):
        # 实现你的聊天逻辑
        pass