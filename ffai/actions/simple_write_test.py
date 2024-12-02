from metagpt.actions.action import Action
import re
import subprocess
from metagpt.logs import logger

class SimpleWriteTest(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    Write {k} unit tests for the given function. The tests should be directly runnable with python3 -c.
    Return ```python your_code_here ``` with NO other texts.
    Make sure to:
    1. Import the function to test
    2. Write test cases that print results
    3. Include all necessary imports
    4. Make it a complete runnable script
    """

    name: str = "SimpleWriteTest"

    async def run(self, context: str, k: int = 3):
        prompt = self.PROMPT_TEMPLATE.format(context=context, k=k)
        rsp = await self._aask(prompt)
        code_text = SimpleWriteTest.parse_code(rsp)
        return code_text
    
    @staticmethod
    def parse_code(rsp):
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text

class SimpleRunTest(Action):
    name: str = "SimpleRunTest"

    async def run(self, code_text: str):
        result = subprocess.run(["python3", "-c", code_text], capture_output=True, text=True)
        code_result = result.stdout
        logger.info(f"{code_result=}")
        return code_result