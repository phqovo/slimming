import random
import string
import urllib.parse
import httpx
from app.core.redis import get_redis
from app.core.config import get_settings

settings = get_settings()


def generate_verification_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))


def save_verification_code(phone: str, code: str, expire: int = 300):
    """保存验证码到Redis"""
    redis_client = get_redis()
    redis_client.setex(f"sms_code:{phone}", expire, code)


def verify_code(phone: str, code: str) -> bool:
    """验证验证码"""
    redis_client = get_redis()
    stored_code = redis_client.get(f"sms_code:{phone}")
    
    if not stored_code:
        return False
    
    if stored_code == code:
        # 验证成功后删除验证码
        redis_client.delete(f"sms_code:{phone}")
        return True
    
    return False


async def send_sms_code(phone: str, code: str) -> bool:
    """
    发送短信验证码（使用短信宝 API）
    
    短信宝 API文档: http://api.smsbao.com/
    
    Args:
        phone: 接收短信的手机号
        code: 验证码
        
    Returns:
        bool: 发送成功返回 True，否则返回 False
    """
    # 调试模式：不真实发送短信
    if settings.SMS_DEBUG_MODE:
        print(f"调试模式 - 未发送短信，验证码: {code}, 手机号: {phone}")
        return False  # 返回 False 表示未真实发送
    
    try:
        # 检查配置
        if not settings.SMS_USERNAME or not settings.SMS_PASSWORD:
            print(f"警告: 短信宝未配置，验证码仅打印到控制台")
            print(f"向 {phone} 发送验证码: {code}")
            return True
        
        # 构造短信内容
        content = f"{settings.SMS_SIGN}您的验证码是{code}，5分钟内有效。"
        
        # URL 编码短信内容
        encoded_content = urllib.parse.quote(content, encoding='utf-8')
        
        # 构造请求 URL
        url = (
            f"http://api.smsbao.com/sms?"
            f"u={settings.SMS_USERNAME}&"
            f"p={settings.SMS_PASSWORD}&"
            f"m={phone}&"
            f"c={encoded_content}"
        )
        
        # 发送请求
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            result = response.text.strip()
            
            # 检查返回结果
            if result == '0':
                print(f"短信发送成功: {phone}")
                return True
            else:
                # 错误码对照
                error_messages = {
                    '30': '错误密码',
                    '40': '账号不存在',
                    '41': '余额不足',
                    '43': 'IP地址限制',
                    '50': '内容含有敏感词',
                    '51': '手机号码不正确'
                }
                error_msg = error_messages.get(result, f'未知错误: {result}')
                print(f"短信发送失败: {phone}, 错误: {error_msg}")
                
                # 开发环境下，即使失败也打印验证码
                if settings.DEBUG:
                    print(f"开发模式 - 向 {phone} 发送验证码: {code}")
                    return True
                    
                return False
                
    except Exception as e:
        print(f"短信发送异常: {str(e)}")
        
        # 开发环境下，即使异常也打印验证码
        if settings.DEBUG:
            print(f"开发模式 - 向 {phone} 发送验证码: {code}")
            return True
            
        return False
