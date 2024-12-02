from metagpt.actions.action import Action
import asyncio
from metagpt.tools.web_browser_engine_playwright import PlaywrightWrapper
from bs4 import BeautifulSoup
import json
from metagpt.logs import logger
import re

class Crawl(Action):
    name: str = "Crawl"
    
    async def run(self, url: str, proxy: str = "http://127.0.0.1:7890") -> str:
        """执行网页爬取操作并返回HTML内容"""
        wrapper = PlaywrightWrapper(browser_type="chromium", proxy=proxy)
        page = await wrapper.run(url)
        html_content = page.html
        
        # 添加预处理步骤
        cleaned_html = self._preprocess_html(html_content)
        return cleaned_html
    
    def _preprocess_html(self, html_content: str) -> str:
        """预处理HTML内容，移除不必要的元素"""
        from bs4 import BeautifulSoup
        from bs4.element import Comment
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除脚本标签
        for script in soup.find_all('script'):
            script.decompose()
        
        # 移除样式标签
        for style in soup.find_all('style'):
            style.decompose()
        
        # 移除注释
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
            
        # 移除头部元数据
        if soup.head:
            soup.head.decompose()
            
        # 移除空白行和多余空格
        cleaned_html = str(soup).strip()
        return cleaned_html

class GenerateSelectors(Action):
    name: str = "GenerateSelectors"
    
    PROMPT_TEMPLATE: str = """
    分析以下HTML内容，生成用于提取{requirement}的CSS选择器。
    请仔细分析HTML结构，找出包含{requirement}的关键元素。

    HTML内容片段:
    {content}
    
    请返回JSON格式的选择器，格式要求：
    1. container: 选择包含所有目标数据的最小容器
    2. item: 如果数据以列表形式存在，这里指定单个数据项的选择器
    3. 根据数据特点，必须包含以下基本字段的选择器：
       - 序号或ID：用于标识每条数据
       - 主要内容：{requirement}的内容，文本形式，使用简单且可靠的选择器，不要使用:contains等伪类选择器
       - 其他你认为有用的字段
    4. 选择器应该尽量简单和通用，使用类名或ID选择器
    
    示例格式:
    {{
        "container": ".data-container",
        "item": ".list-item",
        "序号": ".number",
        "内容": "a",           // 使用类名选择器
    }}

    注意事项：
    1. 不要使用:contains等伪类选择器
    2. 优先使用类名和ID选择器
    3. 选择器要简单且可靠，避免过度限定
    4. 如果有多个匹配项，宁可获取多了也不要漏掉关键信息
    5. 仅返回JSON格式，不要包含任何其他说明文字
    """

    async def run(self, content: str, requirement: str) -> dict:
        """根据需求生成选择器"""
        # 限制内容长度，避免token过长
        max_content_length = 3000
        if len(content) > max_content_length:
            # 提取页面的关键部分
            soup = BeautifulSoup(content, 'html.parser')
            # 尝试找到包含requirement相关内容的部分
            relevant_tags = soup.find_all(text=lambda text: requirement in str(text))
            if relevant_tags:
                # 获取相关标签的父元素们
                relevant_content = ""
                for tag in relevant_tags[:3]:  # 限制数量
                    parent = tag.parent
                    for _ in range(3):  # 向上查找3层父元素
                        if parent:
                            relevant_content += str(parent)
                            parent = parent.parent
                content = relevant_content[:max_content_length]
            else:
                # 如果找不到相关内容，截取中间部分
                content = content[len(content)//4:3*len(content)//4][:max_content_length]

        prompt = self.PROMPT_TEMPLATE.format(
            requirement=requirement,
            content=content
        )
        
        try:
            rsp = await self._aask(prompt)
            # 修改这里：先清理响应文本，再解析成JSON
            cleaned_rsp = self._clean_json_response(rsp)
            selectors = json.loads(cleaned_rsp)
            logger.info(f"生成的选择器: {selectors}")
            
            # 验证返回的选择器格式
            required_keys = ['container']
            if not all(key in selectors for key in required_keys):
                logger.warning(f"生成的选择器缺少必要字段: {required_keys}")
                raise ValueError("Invalid selector format")
                
            return selectors
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"选择器生成失败: {str(e)}")
            # 返回一个通用的错误选择器结构
            return {
                "container": "body",  # 默认容器
                "error": "选择器生成失败，请检查HTML内容或重试"
            }
        
    def _clean_json_response(self, response: str) -> str:
        """清理返回的JSON响应，移除代码块标记和语言标识
        
        Args:
            response: 原始响应文本
        Returns:
            清理后的JSON字符串
        """
        # 移除 ```json 和 ``` 标记
        response = response.strip()
        if response.startswith('```'):
            # 移除第一行（包含```json）
            response = response.split('\n', 1)[1]
        if response.endswith('```'):
            # 移除最后一行
            response = response.rsplit('\n', 1)[0]
        return response.strip()

class ExtractData(Action):
    name: str = "ExtractData"
    
    async def run(self, html_content: str, selectors: dict) -> str:
        """根据选择器提取数据
        
        Args:
            html_content: HTML内容
            selectors: 选择器字典，格式如:
                {
                    "container": "容器选择器",
                    "item": "列表项选择器(可选)",
                    "字段1": "选择器1",
                    "字段2": "选择器2"
                }
        """
        results = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # 查找容器元素
            container = soup.select_one(selectors['container'])
            if not container:
                logger.warning(f"未找到容器元素: {selectors['container']}")
                return json.dumps([], ensure_ascii=False)
            
            # 判断是否为列表类数据
            if 'item' in selectors:
                # 处理列表类数据
                items = container.select(selectors['item'])
                for item in items:
                    data = self._extract_item_data(item, selectors)
                    if data:
                        results.append(data)
            else:
                # 处理单个数据
                data = self._extract_item_data(container, selectors)
                if data:
                    results = data  # 单个数据直接返回对象，而不是列表
                    
            return json.dumps(results, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"数据提取失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    def _extract_item_data(self, element: BeautifulSoup, selectors: dict) -> dict:
        """从单个元素中提取数据
        
        Args:
            element: BeautifulSoup元素
            selectors: 选择器字典
        """
        data = {}
        
        # 遍历所有选择器（排除container和item）
        for field, selector in selectors.items():
            if field in ['container', 'item']:
                continue
                
            try:
                # 添加对空选择器的检查
                if not selector:  # 如果选择器为空，跳过该字段
                    continue
                    
                selected = element.select_one(selector)
                if selected:
                    # 处理不同类型的数据
                    if field.lower().endswith(('链接', 'url', 'href', 'src')):
                        # 处理链接类型
                        value = selected.get('href') or selected.get('src', '')
                        if value and not value.startswith(('http', '/')):
                            # 处理相对路径
                            value = '/' + value.lstrip('/')
                    elif field.lower().endswith(('时间', 'date', 'time')):
                        # 处理时间，去除多余空白
                        value = ' '.join(selected.get_text().split())
                    else:
                        # 处理普通文本
                        value = selected.get_text(strip=True)
                    
                    if value:  # 只添加非空值
                        data[field] = value
                        
            except Exception as e:
                logger.warning(f"提取字段 {field} 失败: {str(e)}")
                continue
                
        return data
