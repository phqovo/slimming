from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime
from app.api.v1 import api_router
from app.core.database import engine, Base, get_db

# 配置日志
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"日志文件: {log_file}")

# 导入所有模型以创建表
from app.models.user import User
from app.models.weight import WeightRecord
from app.models.user_settings import UserSettings
from app.models.daily_history import DailyHistory

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="体重管理平台API",
    description="一个完整的体重管理平台，包含用户认证、体重记录、运动管理、饮食管理等功能",
    version="1.0.0",
    root_path="/health"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs("uploads/avatars", exist_ok=True)
os.makedirs("uploads/exercise", exist_ok=True)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 启动时加载定时任务
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    from app.services.scheduler_service import scheduler_service
    # 加载所有启用的定时任务
    db = next(get_db())
    try:
        scheduler_service.load_all_jobs(db)
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    from app.services.scheduler_service import scheduler_service
    scheduler_service.shutdown()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用体重管理平台API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None
        }
    )


if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
