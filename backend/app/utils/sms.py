import random
import string
import urllib.parse
import json
import httpx
from datetime import datetime, timedelta
from app.core.redis import get_redis
from app.core.config import get_settings

settings = get_settings()


class SMSLimitExceededError(Exception):
    """短信发送次数超出限制异常"""
    def __init__(self, phone: str, count: int, limit: int):
        self.phone = phone
        self.count = count
        self.limit = limit
        super().__init__(f"手机号 {phone} 今日发送次数已达上限 ({limit}/{limit})")


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


async def send_sms_code_aliyun(phone: str, code: str) -> bool:
    """
    使用阿里云通信号码认证服务发送短信验证码

    阿里云通信号码认证 API 文档: https://help.aliyun.com/document_detail/113763.html

    Args:
        phone: 接收短信的手机号
        code: 验证码

    Returns:
        bool: 发送成功返回 True，否则返回 False
    """
    try:
        # 检查配置
        if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
            print(f"警告: 阿里云短信服务未配置，验证码仅打印到控制台")
            print(f"向 {phone} 发送验证码: {code}")
            return True

        if not settings.ALIYUN_SMS_SIGN_NAME or not settings.ALIYUN_SMS_TEMPLATE_CODE:
            print(f"警告: 阿里云短信签名或模板未配置，验证码仅打印到控制台")
            print(f"向 {phone} 发送验证码: {code}")
            return True

        # 导入阿里云 SDK（延迟导入，避免依赖问题）
        try:
            from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
            from alibabacloud_tea_util import models as util_models
        except ImportError as e:
            print(f"错误: 阿里云 SDK 未安装，请运行: pip install alibabacloud-dypnsapi20170525 alibabacloud-credentials")
            print(f"向 {phone} 发送验证码: {code}")
            return True

        # 创建客户端配置
        config = open_api_models.Config(
            access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
            access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
            endpoint='dypnsapi.aliyuncs.com'
        )
        client = DypnsapiClient(config)

        # 构造请求参数
        template_param = json.dumps({"code": code, "min": "5"}, ensure_ascii=False)

        request = dypnsapi_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=settings.ALIYUN_SMS_SIGN_NAME,
            template_code=settings.ALIYUN_SMS_TEMPLATE_CODE,
            template_param=template_param
        )

        runtime = util_models.RuntimeOptions()

        # 发送请求
        resp = client.send_sms_verify_code_with_options(request, runtime)

        if resp.status_code == 200 and resp.body.code == 'OK':
            print(f"阿里云短信发送成功: {phone}")
            return True
        else:
            error_msg = resp.body.message if resp.body else "未知错误"
            print(f"阿里云短信发送失败: {phone}, 错误: {error_msg}")

            # 开发环境下，即使失败也打印验证码
            if settings.DEBUG:
                print(f"开发模式 - 向 {phone} 发送验证码: {code}")
                return True

            return False

    except Exception as e:
        print(f"阿里云短信发送异常: {str(e)}")

        # 开发环境下，即使异常也打印验证码
        if settings.DEBUG:
            print(f"开发模式 - 向 {phone} 发送验证码: {code}")
            return True

        return False


async def send_sms_code_smsbao(phone: str, code: str) -> bool:
    """
    使用短信宝 API 发送短信验证码

    短信宝 API文档: http://api.smsbao.com/

    Args:
        phone: 接收短信的手机号
        code: 验证码

    Returns:
        bool: 发送成功返回 True，否则返回 False
    """
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
                print(f"短信宝短信发送成功: {phone}")
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
                print(f"短信宝短信发送失败: {phone}, 错误: {error_msg}")

                # 开发环境下，即使失败也打印验证码
                if settings.DEBUG:
                    print(f"开发模式 - 向 {phone} 发送验证码: {code}")
                    return True

                return False

    except Exception as e:
        print(f"短信宝短信发送异常: {str(e)}")

        # 开发环境下，即使异常也打印验证码
        if settings.DEBUG:
            print(f"开发模式 - 向 {phone} 发送验证码: {code}")
            return True

        return False


def check_sms_limit(phone: str, daily_limit: int = 5) -> int:
    """
    检查并更新短信发送次数

    Args:
        phone: 手机号
        daily_limit: 每日发送次数限制，默认5次

    Returns:
        int: 当前的发送次数

    Raises:
        SMSLimitExceededError: 超过每日发送限制
    """
    redis_client = get_redis()

    # 使用当前日期作为 key 的一部分，实现每天自动重置
    today = datetime.now().strftime("%Y-%m-%d")
    count_key = f"sms_count:{phone}:{today}"

    # 获取当前已发送次数
    current_count = redis_client.get(count_key)
    current_count = int(current_count) if current_count else 0

    # 检查是否超过限制
    if current_count >= daily_limit:
        raise SMSLimitExceededError(phone, current_count, daily_limit)

    # 增加计数（使用过期时间到当天结束）
    # 计算到今天23:59:59的剩余秒数
    now = datetime.now()
    end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
    expire_seconds = int((end_of_day - now).total_seconds()) + 1

    new_count = redis_client.incr(count_key)

    # 如果是第一次设置，添加过期时间
    if new_count == 1:
        redis_client.expire(count_key, expire_seconds)

    return new_count


async def send_sms_code(phone: str, code: str) -> bool:
    """
    发送短信验证码（根据配置自动选择服务商）

    支持的服务商:
    - aliyun: 阿里云通信号码认证服务（默认）
    - smsbao: 短信宝

    每日发送次数限制: 默认5次/天

    Args:
        phone: 接收短信的手机号
        code: 验证码

    Returns:
        bool: 发送成功返回 True，否则返回 False

    Raises:
        SMSLimitExceededError: 超过每日发送限制
    """
    # 调试模式：不真实发送短信
    if settings.SMS_DEBUG_MODE:
        print(f"调试模式 - 未发送短信，验证码: {code}, 手机号: {phone}")
        return False  # 返回 False 表示未真实发送

    # 检查每日发送次数限制
    try:
        count = check_sms_limit(phone, daily_limit=5)
        print(f"手机号 {phone} 今日第 {count} 次发送验证码")
    except SMSLimitExceededError:
        # 捕获异常并重新抛出，让调用方处理
        raise

    # 根据配置选择短信服务商
    provider = settings.SMS_PROVIDER.lower()

    if provider == 'aliyun':
        return await send_sms_code_aliyun(phone, code)
    elif provider == 'smsbao':
        return await send_sms_code_smsbao(phone, code)
    else:
        print(f"警告: 未知的短信服务商 '{provider}'，请检查配置 SMS_PROVIDER")
        print(f"向 {phone} 发送验证码: {code}")
        return True