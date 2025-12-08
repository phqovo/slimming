"""执行cron调度字段迁移"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库连接
conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST'),
    port=int(os.getenv('MYSQL_PORT', 3306)),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE')
)

try:
    cursor = conn.cursor()
    
    # 读取SQL文件
    with open('migrations/add_cron_schedule_fields.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割并执行每条SQL语句
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    for statement in statements:
        if statement:
            print(f"执行SQL: {statement[:100]}...")
            cursor.execute(statement)
    
    conn.commit()
    print("✓ 数据库迁移成功！")
    
except Exception as e:
    print(f"✗ 迁移失败: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
