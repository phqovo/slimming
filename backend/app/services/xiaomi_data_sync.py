"""小米运动健康数据同步服务"""
import json
import hashlib
import base64
import time
import os
import struct
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx
from Crypto.Cipher import ARC4
from app.services.xiaomi_auth import XiaomiAuth


class XiaomiDataSyncService:
    """小米数据同步服务"""
    
    def __init__(self, token: str, ssecurity: str, cookies: str, auth_id: int = None, db_session = None):
        """
        初始化
        :param token: 格式为 "userID:passToken"
        :param ssecurity: Base64编码的加密密钥
        :param cookies: 登录Cookies
        :param auth_id: 授权记录ID（用于token刷新）
        :param db_session: 数据库会话（用于token刷新）
        """
        self.token = token
        self.ssecurity = base64.b64decode(ssecurity)  # 解码ssecurity
        self.cookies = cookies
        self.auth_id = auth_id
        self.db = db_session
        user_id, pass_token = token.split(':', 1)
        self.user_id = int(user_id)
        self.pass_token = pass_token
        self.client = httpx.Client(timeout=60.0, verify=False)
    
    def _get_fitness_url(self, region: str = "") -> str:
        """获取健康数据API基础URL"""
        if region:
            return f"https://{region}.hlth.io.mi.com"
        return "https://hlth.io.mi.com"
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """计算数据哈希值（用于防重）"""
        # 使用数据的关键字段生成唯一哈希
        hash_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()
    
    def _generate_nonce(self) -> bytes:
        """
        生成nonce（随机8字节 + 4字节时间戳）
        :return: 12字节的nonce
        """
        # 随机8字节
        random_bytes = os.urandom(8)
        # 4字节时间戳（分钟级别）
        ts = int(time.time() / 60)
        ts_bytes = struct.pack('>I', ts)
        return random_bytes + ts_bytes
    
    def _generate_signed_nonce(self, nonce: bytes) -> bytes:
        """
        生成signedNonce = SHA256(ssecurity + nonce)
        :param nonce: nonce字节
        :return: signedNonce字节
        """
        hasher = hashlib.sha256()
        hasher.update(self.ssecurity)
        hasher.update(nonce)
        return hasher.digest()
    
    def _sha1_signature(self, data: str) -> str:
        """
        SHA1签名并Base64编码
        :param data: 要签名的数据
        :return: Base64编码的签名
        """
        hasher = hashlib.sha1()
        hasher.update(data.encode())
        return base64.b64encode(hasher.digest()).decode()
    
    def _rc4_crypt(self, key: bytes, data: bytes) -> bytes:
        """
        RC4加密/解密（先跳过1024字节）
        :param key: 密钥
        :param data: 要加密或解密的数据
        :return: 加密或解密后的数据
        """
        cipher = ARC4.new(key)
        # 跳过1024字节（重要！）
        cipher.encrypt(bytes(1024))
        return cipher.encrypt(data)
    
    def _rc4_encrypt(self, signed_nonce: bytes, data: str) -> str:
        """
        RC4加密并Base64编码
        :param signed_nonce: signedNonce密钥
        :param data: 要加密的数据
        :return: Base64编码的加密结果
        """
        encrypted = self._rc4_crypt(signed_nonce, data.encode())
        return base64.b64encode(encrypted).decode()
    
    def _rc4_decrypt(self, signed_nonce: bytes, data: str) -> str:
        """
        Base64解码并RC4解密
        :param signed_nonce: signedNonce密钥
        :param data: Base64编码的加密数据
        :return: 解密后的字符串
        """
        encrypted_data = base64.b64decode(data)
        decrypted = self._rc4_crypt(signed_nonce, encrypted_data)
        return decrypted.decode()
    
    def _refresh_token(self) -> bool:
        """
        刷新token（当401错误时）
        :return: 是否刷新成功
        """
        if not self.auth_id or not self.db:
            print("❌ 无法刷新token：缺少auth_id或db_session")
            return False
        
        try:
            from app.models.auth_management import AuthManagement
            from app.services.xiaomi_auth import XiaomiAuth
            
            print(f"\n=== Token过期，尝试重新登录 ===")
            
            # 获取授权记录
            auth = self.db.query(AuthManagement).filter(AuthManagement.id == self.auth_id).first()
            if not auth:
                print("❌ 未找到授权记录")
                return False
            
            # 使用token重新登录
            xiaomi_auth = XiaomiAuth()
            result = xiaomi_auth.login_with_token(self.token)
            
            # 更新token信息
            self.token = result['token']
            self.ssecurity = base64.b64decode(result['ssecurity'])
            self.cookies = result['cookies']
            user_id, pass_token = self.token.split(':', 1)
            self.user_id = int(user_id)
            self.pass_token = pass_token
            
            # 更新数据库
            auth.token = result['token']
            auth.ssecurity = result['ssecurity']
            auth.cookies = result['cookies']
            self.db.commit()
            
            print(f"✅ Token刷新成功")
            print(f"  新Token: {self.token[:20]}...")
            
            return True
        except Exception as e:
            print(f"❌ Token刷新失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _request(self, url: str, endpoint: str, params: str, retry_on_401: bool = True) -> Dict:
        """
        发送请求到小米API（完整实现Go版本的签名机制）
        :param url: API基础URL
        :param endpoint: API端点
        :param params: 请求参数（JSON字符串）
        :return: 响应数据
        """
        # 1. 生成nonce（12字节）
        nonce = self._generate_nonce()
        
        # 2. 生成signedNonce = SHA256(ssecurity + nonce)
        signed_nonce = self._generate_signed_nonce(nonce)
        
        # 3. 第一次签名：生成rc4_hash
        # signature_string = "POST&{endpoint}&data={params}&{signedNonce_base64}"
        signed_nonce_b64 = base64.b64encode(signed_nonce).decode()
        signature_str = f"POST&{endpoint}&data={params}&{signed_nonce_b64}"
        rc4_hash = self._sha1_signature(signature_str)
        
        # 4. RC4加密data和rc4_hash
        encrypted_data = self._rc4_encrypt(signed_nonce, params)
        encrypted_hash = self._rc4_encrypt(signed_nonce, rc4_hash)
        
        # 5. 第二次签名：生成signature
        # signature_string = "POST&{endpoint}&data={encrypted_data}&rc4_hash__={encrypted_hash}&{signedNonce_base64}"
        signature_str2 = f"POST&{endpoint}&data={encrypted_data}&rc4_hash__={encrypted_hash}&{signed_nonce_b64}"
        signature = self._sha1_signature(signature_str2)
        
        # 6. 构建请求
        headers = {
            'Cookie': self.cookies,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        full_url = f"{url}{endpoint}"
        
        request_data = {
            'data': encrypted_data,
            'rc4_hash__': encrypted_hash,
            'signature': signature,
            '_nonce': base64.b64encode(nonce).decode()
        }
        
        print(f"\n=== 小米API请求 ===")
        print(f"URL: {full_url}")
        print(f"Nonce: {base64.b64encode(nonce).decode()}")
        print(f"SignedNonce: {signed_nonce_b64}")
        print(f"Signature: {signature}")
        
        response = self.client.post(
            full_url,
            data=request_data,
            headers=headers
        )
        
        print(f"响应状态: {response.status_code}")
        print(f"响应内容长度: {len(response.text)}")
        print(f"响应内容（前500字符）: {response.text[:500]}")
        
        # 特殊处理：HTTP 401时，小米API直接返回明文JSON，不加密
        if response.status_code == 401:
            try:
                result = json.loads(response.text)
                error_code = result.get('code')
                error_msg = result.get('message', 'Unknown error')
                
                # 检查是否为token过期错误
                if error_code == 3 and 'auth err' in error_msg.lower() and retry_on_401:
                    print(f"\n⚠️  检测到Token过期 (HTTP 401, code={error_code}, message={error_msg})")
                    
                    # 尝试刷新token
                    if self._refresh_token():
                        print(f"✅ Token刷新成功，重试请求...")
                        # 重试请求（retry_on_401=False 防止无限循环）
                        return self._request(url, endpoint, params, retry_on_401=False)
                    else:
                        print(f"❌ Token刷新失败")
                        raise Exception(f"Token过期且刷新失败: {error_msg}")
                else:
                    raise Exception(f"API返回错误 (HTTP 401, code={error_code}): {error_msg}")
            except json.JSONDecodeError:
                raise Exception(f"请求失败: {response.status_code}, 响应: {response.text}")
        
        # 其他错误状态码
        if response.status_code != 200:
            raise Exception(f"请求失败: {response.status_code}, 响应: {response.text}")
        
        # RC4解密响应数据
        try:
            response_text = response.text
            decrypted_data = self._rc4_decrypt(signed_nonce, response_text)
            print(f"\n=== 解密后的完整响应 ===")
            print(f"解密数据长度: {len(decrypted_data)}")
            print(f"解密数据: {decrypted_data}")
            
            result = json.loads(decrypted_data)
            print(f"\n=== 解析后的JSON ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"解密失败: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"解密响应失败: {e}")
        
        # 检查响应code（解密成功后再检查）
        if result.get('code') != 0:
            error_code = result.get('code')
            error_msg = result.get('message', 'Unknown error')
            
            # 检查是否为401错误（token过期）
            if error_code == 3 and 'auth err' in error_msg.lower() and retry_on_401:
                print(f"\n⚠️  检测到Token过期 (code={error_code}, message={error_msg})")
                
                # 尝试刷新token
                if self._refresh_token():
                    print(f"✅ Token刷新成功，重试请求...")
                    # 重试请求（retry_on_401=False 防止无限循环）
                    return self._request(url, endpoint, params, retry_on_401=False)
                else:
                    print(f"❌ Token刷新失败")
                    raise Exception(f"Token过期且刷新失败: {error_msg}")
            else:
                raise Exception(f"API返回错误 (code={error_code}): {error_msg}")
        
        return result.get('result', result)
    
    def get_sleep_records(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        获取睡眠记录
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 睡眠记录列表
        """
        import sys
        print(f"\n========== 获取睡眠数据 ==========", flush=True)
        print(f"开始时间: {start_time} ({int(start_time.timestamp())})", flush=True)
        print(f"结束时间: {end_time} ({int(end_time.timestamp())})", flush=True)
        sys.stdout.flush()
        
        params = json.dumps({
            "start_time": int(start_time.timestamp()),
            "end_time": int(end_time.timestamp()),
            "key": "sleep"
        })
        
        all_records = []
        next_key = ""
        
        while True:
            if next_key:
                request_params = json.dumps({
                    "start_time": int(start_time.timestamp()),
                    "end_time": int(end_time.timestamp()),
                    "key": "sleep",
                    "next_key": next_key
                })
            else:
                request_params = params
            
            result = self._request(
                self._get_fitness_url(),
                "/app/v1/data/get_fitness_data_by_time",
                request_params
            )
            
            print(f"\n小米API返回结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            for idx, item in enumerate(result.get('data_list', [])):
                try:
                    print(f"\n--- 原始记录 #{idx + 1} ---")
                    print(f"完整item: {json.dumps(item, indent=2, ensure_ascii=False)}")
                    
                    value = json.loads(item['value'])
                    print(f"解析后的value: {json.dumps(value, indent=2, ensure_ascii=False)}")
                    
                    value['data_hash'] = self._calculate_data_hash(item)
                    value['source_id'] = str(item.get('time', ''))
                    all_records.append(value)
                except Exception as e:
                    print(f"解析记录失败: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            if not result.get('has_more', False):
                break
            
            next_key = result.get('next_key', '')
            if not next_key:
                break
        
        print(f"\n总共获取到 {len(all_records)} 条睡眠记录")
        return all_records
    
    def get_exercise_records(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        获取运动记录
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 运动记录列表
        """
        params = json.dumps({
            "start_time": int(start_time.timestamp()),
            "end_time": int(end_time.timestamp())
        })
        
        all_records = []
        next_key = ""
        
        while True:
            if next_key:
                request_params = json.dumps({
                    "start_time": int(start_time.timestamp()),
                    "end_time": int(end_time.timestamp()),
                    "next_key": next_key
                })
            else:
                request_params = params
            
            result = self._request(
                self._get_fitness_url(),
                "/app/v1/data/get_sport_records_by_time",
                request_params
            )
            
            for item in result.get('sport_records', []):
                try:
                    value = json.loads(item.get('value', '{}'))
                    value['data_hash'] = self._calculate_data_hash(item)
                    value['source_id'] = str(item.get('time', ''))
                    value['category'] = item.get('category', '')
                    all_records.append(value)
                except:
                    continue
            
            if not result.get('has_more', False):
                break
            
            next_key = result.get('next_key', '')
            if not next_key:
                break
        
        return all_records
    
    def get_weight_records(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        获取体重记录
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 体重记录列表
        """
        print(f"\n========== 获取体重数据 ==========")
        print(f"开始时间: {start_time} ({int(start_time.timestamp())})")
        print(f"结束时间: {end_time} ({int(end_time.timestamp())})")
        
        params = json.dumps({
            "start_time": int(start_time.timestamp()),
            "end_time": int(end_time.timestamp()),
            "key": "weight"
        })
        
        all_records = []
        next_key = ""
        
        while True:
            if next_key:
                request_params = json.dumps({
                    "start_time": int(start_time.timestamp()),
                    "end_time": int(end_time.timestamp()),
                    "key": "weight",
                    "next_key": next_key
                })
            else:
                request_params = params
            
            result = self._request(
                self._get_fitness_url(),
                "/app/v1/data/get_fitness_data_by_time",
                request_params
            )
            
            print(f"\n小米API返回结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            for idx, item in enumerate(result.get('data_list', [])):
                try:
                    print(f"\n--- 原始记录 #{idx + 1} ---")
                    print(f"完整item: {json.dumps(item, indent=2, ensure_ascii=False)}")
                    
                    value = json.loads(item['value'])
                    print(f"解析后的value: {json.dumps(value, indent=2, ensure_ascii=False)}")
                    
                    value['data_hash'] = self._calculate_data_hash(item)
                    value['source_id'] = str(item.get('time', ''))
                    value['timestamp'] = item.get('time', 0)
                    all_records.append(value)
                except Exception as e:
                    print(f"解析记录失败: {e}")
                    continue
            
            if not result.get('has_more', False):
                break
            
            next_key = result.get('next_key', '')
            if not next_key:
                break
        
        print(f"\n总共获取到 {len(all_records)} 条体重记录")
        return all_records
    
    def get_step_records(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        获取步数记录
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 步数记录列表
        """
        params = json.dumps({
            "start_time": int(start_time.timestamp()),
            "end_time": int(end_time.timestamp()),
            "key": "steps"
        })
        
        result = self._request(
            self._get_fitness_url(),
            "/app/v1/data/get_fitness_data_by_time",
            params
        )
        
        records = []
        for item in result.get('data_list', []):
            try:
                value = json.loads(item['value'])
                value['data_hash'] = self._calculate_data_hash(item)
                value['source_id'] = str(item.get('time', ''))
                records.append(value)
            except:
                continue
        
        return records
    
    def close(self):
        """关闭HTTP客户端"""
        self.client.close()
