from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "slimming_db"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    # 短信配置
    SMS_PROVIDER: str = "aliyun"  # 短信服务提供商: aliyun=阿里云通信号码认证, smsbao=短信宝
    SMS_DEBUG_MODE: bool = False  # True=调试模式（不发短信）, False=正常模式

    # 阿里云通信号码认证服务配置
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = ""  # 短信签名
    ALIYUN_SMS_TEMPLATE_CODE: str = ""  # 验证码模板CODE

    # 短信宝配置（备用）
    SMS_USERNAME: str = ""
    SMS_PASSWORD: str = ""  # MD5后的密码或ApiKey
    SMS_SIGN: str = "【短信宝】"  # 短信签名
    
    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    STORAGE_TYPE: int = 2  # 1=本地存储, 2=七牛云存储
    
    # 七牛云配置
    QINIU_ACCESS_KEY: str = ""
    QINIU_SECRET_KEY: str = ""
    QINIU_BUCKET_NAME: str = ""
    QINIU_DOMAIN: str = ""  # 七牛云绑定的域名（如 https://cdn.yourdomain.com）
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""  # 留空则使用官方 API: https://api.openai.com
    
    # Google Gemini配置
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = ""  # 留空则使用官方 API: https://generativelanguage.googleapis.com
    
    # OAuth配置
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    QQ_APP_ID: str = ""
    QQ_APP_KEY: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
