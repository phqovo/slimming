"""
小米运动健康登录服务
参考 SmartScaleConnect 项目的 Go 实现，使用 Python 重写
"""
import hashlib
import base64
import json
import random
import string
from typing import Dict, Optional
import httpx


class XiaomiAuth:
    """小米运动健康认证类"""
    
    def __init__(self, app_type: str = "miothealth"):
        """
        初始化
        :param app_type: 应用类型，miothealth=小米运动健康, xiaomiio=小米智能家居
        """
        self.app_type = app_type
        self.sid = app_type
        # 禁用SSL验证，避免证书验证失败
        self.client = httpx.Client(timeout=60.0, verify=False)
        
        # 登录后的关键数据
        self.user_id: Optional[int] = None
        self.pass_token: Optional[str] = None
        self.ssecurity: Optional[bytes] = None
        self.cookies: Optional[str] = None
    
    def login(self, username: str, password: str, callback_url: Optional[str] = None) -> Dict:
        """
        登录小米账号
        :param username: 用户名（手机号/邮箱）
        :param password: 密码
        :param callback_url: 自定义回调地址，用于二次验证后的跳转
        :return: 包含 token, ssecurity, cookies 的字典，或需要二次验证的信息
        """
        # 第一步：获取登录参数
        res1 = self._service_login_step1(callback_url)
        
        # 第二步：提交账号密码
        res2 = self._service_login_step2(res1, username, password)
        
        # 检查是否需要二次验证
        if 'notificationUrl' in res2 and not res2.get('location'):
            return {
                'need_verify': True,
                'notification_url': res2['notificationUrl'],
                'message': '需要二次验证，请通过手机或邮箱完成验证'
            }
        
        # 第三步：获取 cookies
        self._service_login_step3(res2['location'])
        
        # 返回登录信息
        return {
            'need_verify': False,
            'token': self.token,
            'user_id': self.user_id,
            'pass_token': self.pass_token,
            'ssecurity': base64.b64encode(self.ssecurity).decode() if self.ssecurity else None,
            'cookies': self.cookies
        }
    
    def _service_login_step1(self, callback_url: Optional[str] = None) -> Dict:
        """
        第一步：获取登录参数
        :param callback_url: 自定义回调地址，用于二次验证后的跳转
        """
        url = f"https://account.xiaomi.com/pass/serviceLogin?_json=true&sid={self.sid}"
        if callback_url:
            # 如果指定了回调地址，添加到请求中
            from urllib.parse import quote
            url += f"&callback={quote(callback_url)}"
        
        response = self.client.get(url)
        body = self._read_login_response(response)
        
        res1 = json.loads(body)
        print(f"Step1 response: {json.dumps(res1, ensure_ascii=False)}")
        print(f"Callback parameter: {res1.get('callback')}")
        
        # 不检查 step1 的错误状态，直接返回
        # 因为即使 result=error，也可能包含必要的 _sign 等字段
        return res1
    
    def _service_login_step2(self, res1: Dict, username: str, password: str) -> Dict:
        """第二步：提交账号密码"""
        # MD5 加密密码
        hash_password = hashlib.md5(password.encode()).hexdigest().upper()
        
        # 从 res1 或 self.sid 获取 sid
        sid = res1.get('sid') or self.sid
        callback = res1.get('callback', '')
        _sign = res1.get('_sign', '')
        qs = res1.get('qs', '')
        
        # 检查必要字段
        if not _sign:
            print(f"警告: step1 响应中缺少 _sign 字段")
            print(f"完整 res1: {json.dumps(res1, ensure_ascii=False)}")
            raise ValueError(f"登录失败：step1 响应格式异常，缺少 _sign 字段")
        
        form_data = {
            '_json': 'true',
            'hash': hash_password,
            'sid': sid,
            'callback': callback,
            '_sign': _sign,
            'qs': qs,
            'user': username
        }
        
        # 生成随机 deviceId
        device_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        headers = {
            'Cookie': f'deviceId={device_id}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = self.client.post(
            'https://account.xiaomi.com/pass/serviceLoginAuth2',
            data=form_data,
            headers=headers
        )
        
        body = self._read_login_response(response)
        res2 = json.loads(body)
        
        # 调试输出 - 完整打印响应
        print(f"Step2 response (full): {json.dumps(res2, ensure_ascii=False)}")
        
        # 检查响应中是否包含错误
        if 'code' in res2 and res2['code'] != 0:
            error_desc = res2.get('desc', '未知错误')
            error_code = res2.get('code')
            
            # 特殊处理验证码错误（87001）
            if error_code == 87001 or 'captchaUrl' in res2:
                raise ValueError(
                    "需要图形验证码验证。请尝试以下方法：\n"
                    "1. 在小米账号官网（account.xiaomi.com）登录一次\n"
                    "2. 使用小米官方APP登录一次\n"
                    "3. 等待几分钟后重试\n"
                    "4. 确保账号密码正确"
                )
            
            raise ValueError(f"登录失败: {error_desc}")
        
        # 如果需要二次验证，直接返回，不检查 passToken
        if 'notificationUrl' in res2 and not res2.get('location'):
            return res2
        
        # 保存登录信息
        if 'passToken' not in res2:
            raise ValueError(f"登录失败：账号或密码错误")
        
        self.pass_token = res2['passToken']
        self.ssecurity = base64.b64decode(res2['ssecurity'])
        self.user_id = res2['userId']
        
        return res2
    
    def _service_login_step3(self, location: str):
        """第三步：获取 cookies"""
        response = self.client.get(location)
        
        # 提取所有 cookies
        cookies_list = []
        for cookie_header in response.headers.get_list('set-cookie'):
            cookie = cookie_header.split(';')[0]
            cookies_list.append(cookie)
        
        self.cookies = '; '.join(cookies_list)
    
    @staticmethod
    def _read_login_response(response: httpx.Response) -> bytes:
        """读取登录响应"""
        body = response.read()
        prefix = b'&&&START&&&'
        
        if not body.startswith(prefix):
            raise ValueError("Invalid login response format")
        
        return body[len(prefix):]
    
    @property
    def token(self) -> Optional[str]:
        """获取 token (格式: userID:passToken)"""
        if self.user_id and self.pass_token:
            return f"{self.user_id}:{self.pass_token}"
        return None
    
    def login_with_token(self, token: str) -> Dict:
        """
        使用 token 登录（免密登录）
        :param token: 格式为 "userID:passToken"
        :return: 包含 token, ssecurity, cookies 的字典
        """
        user_id, pass_token = token.split(':', 1)
        
        headers = {
            'Cookie': f'userId={user_id}; passToken={pass_token}'
        }
        
        url = f"https://account.xiaomi.com/pass/serviceLogin?_json=true&sid={self.sid}"
        response = self.client.get(url, headers=headers)
        
        body = self._read_login_response(response)
        res2 = json.loads(body)
        
        # 保存登录信息
        self.pass_token = res2['passToken']
        self.ssecurity = base64.b64decode(res2['ssecurity'])
        self.user_id = res2['userId']
        
        # 获取 cookies
        self._service_login_step3(res2['location'])
        
        return {
            'token': self.token,
            'user_id': self.user_id,
            'pass_token': self.pass_token,
            'ssecurity': base64.b64encode(self.ssecurity).decode() if self.ssecurity else None,
            'cookies': self.cookies
        }
    
    def close(self):
        """关闭 HTTP 客户端"""
        self.client.close()
    
    def check_verify_status(self, username: str, password: str) -> Dict:
        """
        检查二次验证状态
        :param username: 用户名
        :param password: 密码
        :return: 验证结果
        """
        # 重新执行登录流程，检查是否已完成验证
        return self.login(username, password)
