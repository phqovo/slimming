"""
初始化脚本：为所有已有用户更新健康数据
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.utils.health_calculator import update_user_health_stats


def init_all_users_health_stats():
    """为所有用户初始化健康数据"""
    db = SessionLocal()
    try:
        # 获取所有用户
        users = db.query(User).all()
        
        print(f"开始初始化 {len(users)} 个用户的健康数据...")
        
        success_count = 0
        for user in users:
            if update_user_health_stats(db, user.id):  # pyright: ignore[reportArgumentType]
                success_count += 1
                print(f"✓ 用户 {user.phone} (ID: {user.id}) 健康数据更新成功")
            else:
                print(f"✗ 用户 {user.phone} (ID: {user.id}) 健康数据更新失败")
        
        print(f"\n完成！成功更新 {success_count}/{len(users)} 个用户")
        
    except Exception as e:
        print(f"初始化失败: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    init_all_users_health_stats()
