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
        # 获取最新的测试结果消息
        test_messages = self.rc.memory.get_by_action(SimpleRunTest)
        if not test_messages:
            return None
            
        test_result = test_messages[-1]
        # 执行代码评审
        review_action = SimpleWriteReview()
        review_result = await review_action.run(test_result.content)
        
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