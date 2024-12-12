from metagpt.actions.action import Action


class SimpleWriteReview(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    审查需求和函数，并返回以下格式，不要关注测试案例，仅关注测试结果，对于Status，仅返回LGTM或LBTM:
    ---
    Review Comments:
    1. 功能完整性 - 函数是否完全实现了需求
    2. 代码正确性 - 逻辑是否存在问题
    3. 边界处理 - 是否处理了边界情况
    4. 性能考虑 - 实现是否高效
    5. 代码风格 - 是否符合规范
    
    Status:
    LGTM or LBTM (Looks Good/Bad To Me)
    ---
    """

    name: str = "SimpleWriteReview"

    async def run(self, context: str):
        prompt = self.PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)
        return rsp