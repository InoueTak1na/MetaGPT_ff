from typing import Dict, Union, Type
from metagpt.actions import Action
import ast
from metagpt.logs import logger

class OutputParser:
    @staticmethod
    def extract_struct(text: str, data_type: Union[Type[list], Type[dict]]) -> Union[list, dict]:
        """
        返回:
        - 如果提取和解析成功，它将返回相应的数据结构(列表或字典)。
        - 如果提取失败或解析遇到错误，则抛出异常。
        """
        start_index = text.find("[" if data_type is list else "{")
        end_index = text.rfind("]" if data_type is list else "}")
        if start_index != -1 and end_index != -1:
            structure_text = text[start_index:end_index+1]
            
            try:
                result = ast.literal_eval(structure_text)
                if isinstance(result, data_type):
                    return result
                else:
                    raise ValueError(f"解析结果类型不匹配，期望类型: {data_type}, 实际类型: {type(result)}")
            except Exception as e:
                raise ValueError(f"解析失败: {e}")
        else:
            logger.error(f"未在文本中找到对应的{data_type.__name__}结构")
            return [] if data_type is list else {}

class WriteDirectory(Action):
    """
    用于编写教程目录的动作类
    参数:
        name: 动作的名称
        language: 输出的语言，默认为"Chinese"
    """
    name: str = "WriteDirectory"
    language: str = "Chinese"

    async def run(self, topic: str, *args, **kwargs) -> Dict:
        """
        根据主题执行生成教程目录的教程。
        参数:
            topic: 教程的主题
        返回:
            教程目录信息，包括{{"title": "xxx", "directory": [{{"dir 1": ["sub dir 1", "sub dir 2"]}}, {{"dir 2": ["sub dir 1", "sub dir 2"]}}]}}.
        """
        COMMON_PROMPT = """
        你现在是互联网领域的经验丰富的技术专业人员。现在需要你撰写一个关于"{topic}"的技术教程。
        """

        DIRECTORY_PROMPT = COMMON_PROMPT + """
        请按照以下要求提供本教程的具体目录:
        1. 输出必须严格符合指定语言，{language}
        2. 回答必须严格按照字典格式，如：{{"title": "xxx", "directory": [{{"dir 1": ["sub dir 1", "sub dir 2"]}}, {{"dir 2": ["sub dir 1", "sub dir 2"]}}]}}
        3. 目录应尽可能具体和充分，包括一级和二级目录。二级目录在数组中。
        4. 不要有额外的空格或换行符。
        5. 每个目录标题都具有实际意义。
        """

        prompt = DIRECTORY_PROMPT.format(topic=topic, language=self.language)
        response = await self.llm.aask(prompt)
        return OutputParser.extract_struct(response, dict)
    
class WriteContent(Action):
    """
    用于编写教程内容的动作类
    参数:
        name: 动作的名称
        directory: 要写的内容
        language: 输出的语言，默认为"Chinese"
    """
    name: str = "WriteContent"
    directory: dict = dict()
    language: str = "Chinese"

    async def run(self, topic: str, *args, **kwargs) -> str:
        """
        根据教程目录和主题撰写教程内容。
        参数:
            topic: 教程的主题
        返回:
            编写好的教程内容
        """
        COMMON_PROMPT = """
        你现在是一个互联网领域经验丰富的技术专家，我需要你以"{topic}"为主题编写一个技术教程。
        """

        CONTENT_PROMPT = COMMON_PROMPT + """
        现在我将为你提供该主题的模块目录标题。
        请输出此标题的详细原理内容。
        如果有代码示例，请按照标准代码规范提供。
        没有代码示例则不需要提供。

        该主题的模块目录标题如下:
        {directory}

        严格按照以下要求限制输出:
        1. 遵循Markdown语法格式进行布局。
        2. 如果有代码示例，必须遵循标准语法规范，具备文档注释，并以代码块形式显示。
        3. 输出必须严格使用指定语言{language}。
        4. 不得有冗余输出，包括总结性陈述。
        5. 严禁输出主题＂{topic}"
        """

        prompt = CONTENT_PROMPT.format(
            topic=topic, directory=self.directory, language=self.language)
        response = await self.llm.aask(msg=prompt)
        return response
