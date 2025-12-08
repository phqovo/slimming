# 环境配置说明

本项目使用环境变量管理敏感配置信息。

## 快速开始

1. 复制环境变量示例文件：
```bash
cp backend/.env.example backend/.env
```

2. 编辑 `backend/.env` 文件，填入你的实际配置：
   - MySQL 数据库连接信息
   - Redis 连接信息
   - JWT 密钥（建议使用随机生成的强密钥）
   - 短信服务配置（如需短信验证码功能）
   - 七牛云配置（如需云存储功能）
   - OpenAI API Key（如需AI功能）
   - QQ/微信登录配置（如需第三方登录）

## 配置项说明

### 必需配置
- `MYSQL_*`: MySQL数据库配置
- `REDIS_*`: Redis缓存配置
- `SECRET_KEY`: JWT密钥，**务必修改为随机字符串**

### 可选配置
- `SMS_*`: 短信验证码服务（使用短信宝）
- `QINIU_*`: 七牛云存储（图片上传）
- `OPENAI_API_KEY`: OpenAI服务（AI功能）
- `QQ_*` / `WECHAT_*`: 第三方登录

## 安全提醒

⚠️ **重要**: 
- `.env` 文件已在 `.gitignore` 中，不会被提交到Git
- 请勿将 `.env` 文件分享给他人
- 生产环境请使用强密码和随机密钥
- 定期更新敏感凭据

## 生成安全的SECRET_KEY

使用Python生成随机密钥：
```python
import secrets
print(secrets.token_urlsafe(32))
```
