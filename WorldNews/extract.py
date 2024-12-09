from bs4 import BeautifulSoup

def extract_news(html):
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []
    
    # 查找所有新闻容器
    results = soup.find_all('div', class_='result c-container xpath-log new-pmd')
    
    for result in results:
        item = {}
        
        # 提取标题和链接
        title_tag = result.find('a', attrs={'data-click': True})
        if title_tag:
            item['title'] = title_tag.get_text(strip=True)
            item['link'] = title_tag.get('href')
        
        # 提取内容
        content_spans = result.find_all('span', class_=lambda x: x and ('content-right_' in x))
        if content_spans:
            item['content'] = content_spans[0].get_text(strip=True)
            
        if item:
            news_items.append(item)
            
    return news_items

# 使用示例:
with open('WorldNews/news.html', 'r', encoding='utf-8') as f:
    html_content = f.read()
    news_items = extract_news(html_content)
    for item in news_items:
        print(f"标题: {item.get('title')}")
        print(f"链接: {item.get('link')}")
        print(f"内容: {item.get('content')}")
    print("---")