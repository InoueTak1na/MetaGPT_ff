from metagpt.actions import Action
import mysql.connector

class CreateDB(Action):
    name: str = "CreateDB"
    goal: str = "创建数据库"
    input: str = "数据库名称"
    output: str = "数据库创建状态"

    async def run(self) -> str:
        try:
            db_name = "world_news"
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hjp12459"
            )
            cursor = conn.cursor()
            
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if db_name in databases:
                cursor.execute(f"USE {db_name}")
                # 检查表是否存在
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                if 'news' in tables:
                    cursor.close()
                    conn.close()
                    return f"数据库 {db_name} 和表 news 已存在,无需创建"
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # 创建news表
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS news (
                news_data_id BIGINT PRIMARY KEY,
                source_name VARCHAR(32),
                source_url VARCHAR(1024),
                source_type SMALLINT,
                summary_cn VARCHAR(1024),
                summary_en VARCHAR(1024),
                content_cn TEXT,
                content_en TEXT,
                create_time TIMESTAMP,
                title_cn VARCHAR(255),
                title_en VARCHAR(255),
                source_key VARCHAR(255),
                secondary_classification_id BIGINT,
                secondary_classification_name VARCHAR(255),
                emotional_tendencies INT,
                creator_name VARCHAR(255),
                updater_name VARCHAR(255),
                news_time TIMESTAMP,
                entity_extraction VARCHAR(1024),
                push_fs_status INT COMMENT '推送飞书状态，空：未推送，1：已推送'
            )"""
            
            cursor.execute(create_table_sql)
            conn.commit()
            cursor.close()
            conn.close()
            
            return f"数据库 {db_name} 和表 news 创建成功"
            
        except Exception as e:
            return f"创建失败: {str(e)}"

class InsertNews(Action):
    name: str = "InsertNews"
    goal: str = "插入新闻基础数据"
    input: str = "新闻数据"
    output: str = "插入状态"

    async def run(self, news_data: dict) -> str:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hjp12459",
                database="world_news"  # 添加数据库名
            )
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO news (
                news_data_id, source_url, title_cn, source_name, 
                create_time, news_time
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            """
            values = (
                news_data['id'],
                news_data['url'],
                news_data['title'],
                news_data['source'],
                news_data['create_time'],
                news_data['news_time']
            )
            
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
            return "基础数据插入成功"
        except Exception as e:
            return f"插入失败: {str(e)}"

class UpdateNewsContent(Action):
    name: str = "UpdateNewsContent"
    goal: str = "更新新闻正文内容"
    input: str = "新闻ID和正文内容"
    output: str = "更新状态"

    async def run(self, news_id: int, content: dict) -> str:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hjp12459",
                database="world_news"
            )
            cursor = conn.cursor()
            
            sql = """
            UPDATE news 
            SET content_cn = %s, content_en = %s
            WHERE news_data_id = %s
            """
            values = (content['content_cn'], content['content_en'], news_id)
            
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
            return "正文更新成功"
        except Exception as e:
            return f"更新失败: {str(e)}"

class UpdateNewsAnalysis(Action):
    name: str = "UpdateNewsAnalysis"
    goal: str = "更新新闻分析结果"
    input: str = "新闻ID和分析结果"
    output: str = "更新状态"

    async def run(self, news_id: int, analysis: dict) -> str:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hjp12459",
                database="world_news"
            )
            cursor = conn.cursor()
            
            sql = """
            UPDATE news 
            SET emotional_tendencies = %s,
                entity_extraction = %s,
                secondary_classification_name = %s
            WHERE news_data_id = %s
            """
            values = (
                analysis['emotion'],
                analysis['entities'],
                analysis['classification'],
                news_id
            )
            
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
            return "分析结果更新成功"
        except Exception as e:
            return f"更新失败: {str(e)}"

class GetUnprocessedUrls(Action):
    name: str = "GetUnprocessedUrls"
    goal: str = "获取未处理的URL列表"
    input: str = "处理类型"
    output: str = "URL列表"

    async def run(self, process_type: str) -> list:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hjp12459",
                database="world_news"
            )
            cursor = conn.cursor(dictionary=True)
            
            if process_type == "content":
                sql = """
                SELECT news_data_id, source_url 
                FROM news 
                WHERE content_cn IS NULL
                """
            elif process_type == "analysis":
                sql = """
                SELECT news_data_id, content_cn 
                FROM news 
                WHERE content_cn IS NOT NULL 
                AND emotional_tendencies IS NULL
                """
                
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            return f"查询失败: {str(e)}"

class QueryNews(Action):
    name: str = "QueryNews"
    goal: str = "查询新闻数据"
    input: str = "查询条件"
    output: str = "查询结果"

    async def run(self, query: str) -> str:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hjp12459"
            )
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            return f"查询失败: {str(e)}"

class CallRole(Action):
    name: str = "CallRole"
    goal: str = "调用角色"
    input: str = "角色名称"
    output: str = "调用结果"

    