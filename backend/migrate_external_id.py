#!/usr/bin/env python3
"""添加 external_id 字段迁移脚本"""

from sqlalchemy import text
from app.core.database import engine

def migrate():
    with open('migrations/add_external_id_fields.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # 分割SQL语句
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    with engine.connect() as conn:
        for stmt in statements:
            if stmt:
                print(f"执行: {stmt[:80]}...")
                try:
                    conn.execute(text(stmt))
                    conn.commit()
                    print("✓ 成功")
                except Exception as e:
                    print(f"✗ 失败: {e}")
                    conn.rollback()
    
    print("\n数据库迁移完成！")

if __name__ == "__main__":
    migrate()
