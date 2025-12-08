"""执行OAuth字段迁移"""
from app.core.database import engine
from sqlalchemy import text

sql_statements = [
    "ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(100) UNIQUE COMMENT '微信openid'",
    "ALTER TABLE users ADD COLUMN wechat_unionid VARCHAR(100) COMMENT '微信unionid'",
    "ALTER TABLE users ADD COLUMN qq_openid VARCHAR(100) UNIQUE COMMENT 'QQ openid'",
    "ALTER TABLE users ADD COLUMN oauth_avatar VARCHAR(500) COMMENT '第三方原始头像URL'",
    "ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) NULL",
]

try:
    with engine.connect() as conn:
        for statement in sql_statements:
            try:
                conn.execute(text(statement))
                conn.commit()
                print(f"✅ 执行成功: {statement[:60]}...")
            except Exception as e:
                if "Duplicate column" in str(e) or "already exists" in str(e):
                    print(f"⏭️  字段已存在，跳过: {statement[:60]}...")
                else:
                    print(f"❌ 执行失败: {e}")
    print("\n✅ 数据库迁移完成！")
except Exception as e:
    print(f"❌ 迁移失败: {e}")
