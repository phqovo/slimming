"""
七牛云存储工具类
"""
from qiniu import Auth, put_data, BucketManager
from app.core.config import get_settings
import uuid
from datetime import datetime
from typing import Optional

settings = get_settings()


class QiniuStorage:
    """七牛云存储管理类"""
    
    def __init__(self):
        self.access_key = settings.QINIU_ACCESS_KEY
        self.secret_key = settings.QINIU_SECRET_KEY
        self.bucket_name = settings.QINIU_BUCKET_NAME
        self.domain = settings.QINIU_DOMAIN
        self.auth = Auth(self.access_key, self.secret_key)
    
    def get_upload_token(self, key: Optional[str] = None, expires: int = 3600) -> str:
        """
        获取上传凭证
        
        Args:
            key: 文件名（不指定则由七牛自动生成）
            expires: 凭证有效期（秒）
            
        Returns:
            上传凭证
        """
        return self.auth.upload_token(self.bucket_name, key, expires)
    
    def upload_data(self, data: bytes, file_ext: str, folder: str = "") -> dict:
        """
        上传文件数据到七牛云
        
        Args:
            data: 文件二进制数据
            file_ext: 文件扩展名（如 .jpg）
            folder: 存储文件夹（如 avatars/）
            
        Returns:
            dict: {
                "success": bool,
                "url": str,  # 完整访问URL
                "key": str   # 七牛云存储的key
            }
        """
        try:
            # 生成唯一文件名
            filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
            key = f"{folder}{filename}" if folder else filename
            
            # 获取上传凭证
            token = self.get_upload_token(key)
            
            # 上传文件
            ret, info = put_data(token, key, data)
            
            if info.status_code == 200:
                # 上传成功，返回访问URL
                file_url = f"{self.domain}/{key}"
                return {
                    "success": True,
                    "url": file_url,
                    "key": key
                }
            else:
                print(f"七牛云上传失败: {info}")
                return {
                    "success": False,
                    "url": "",
                    "key": "",
                    "error": info.text_body
                }
                
        except Exception as e:
            print(f"七牛云上传异常: {str(e)}")
            return {
                "success": False,
                "url": "",
                "key": "",
                "error": str(e)
            }
    
    def delete_file(self, key: str) -> bool:
        """
        删除七牛云上的文件
        
        Args:
            key: 文件的存储key
            
        Returns:
            bool: 是否删除成功
        """
        try:
            bucket = BucketManager(self.auth)
            ret, info = bucket.delete(self.bucket_name, key)
            return info.status_code == 200
        except Exception as e:
            print(f"七牛云删除文件失败: {str(e)}")
            return False
    
    def get_file_url(self, key: str) -> str:
        """
        根据文件key获取访问URL
        
        Args:
            key: 文件的存储key
            
        Returns:
            完整的访问URL
        """
        return f"{self.domain}/{key}"


# 创建全局实例
qiniu_storage = QiniuStorage()
