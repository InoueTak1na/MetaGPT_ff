from metagpt.roles.role import Role
from ffai.actions.simple_wirte_review import SimpleWriteReview
from ffai.actions.simple_write_test import SimpleRunTest
from metagpt.schema import Message
from ffai.actions.simple_write_test import SimpleRunTest

class SimpleReviewer(Role):
    name: str = "Charlie"
    profile: str = "SimpleReviewer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteReview])
        self._watch([SimpleRunTest])
        
    async def _act(self) -> Message:
        context = self.get_memories()
        # 执行代码评审
        review_action = SimpleWriteReview()
        review_result = await review_action.run(context)
        
        # 根据评审结果发送消息
        if "LBTM" in review_result:
            return Message(
                content=review_result,
                role=self.profile,
                cause_by=SimpleWriteReview,
                send_to="Alice"  # SimpleCoder
            )
        return Message(
            content=review_result,
            role=self.profile,
            cause_by=SimpleWriteReview,
        )