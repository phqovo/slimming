"""
统一文件存储工具
支持本地存储和七牛云存储
"""
import os
import uuid
import aiofiles
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()


async def upload_file(data: bytes, file_ext: str, folder: str = "") -> dict:
    """
    统一文件上传接口，根据配置选择存储方式
    
    Args:
        data: 文件二进制数据
        file_ext: 文件扩展名（如 .jpg）
        folder: 存储文件夹（如 avatars/）
        
    Returns:
        dict: {
            "success": bool,
            "url": str,  # 完整访问URL
            "key": str   # 存储的key或路径
        }
    """
    if settings.STORAGE_TYPE == 1:
        # 本地存储
        return await _upload_to_local(data, file_ext, folder)
    elif settings.STORAGE_TYPE == 2:
        # 七牛云存储
        return await _upload_to_qiniu(data, file_ext, folder)
    else:
        return {
            "success": False,
            "url": "",
            "key": "",
            "error": f"不支持的存储类型: {settings.STORAGE_TYPE}"
        }


async def _upload_to_local(data: bytes, file_ext: str, folder: str = "") -> dict:
    """
    上传到本地存储
    """
    try:
        # 生成文件名
        filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
        
        # 构建存储路径
        upload_dir = os.path.join(settings.UPLOAD_DIR, folder.rstrip('/'))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(data)
        
        # 返回访问URL（需要通过Nginx或FastAPI的静态文件服务访问）
        url = f"/health/uploads/{folder}{filename}"
        
        return {
            "success": True,
            "url": url,
            "key": file_path
        }
    except Exception as e:
        print(f"本地存储上传失败: {str(e)}")
        return {
            "success": False,
            "url": "",
            "key": "",
            "error": str(e)
        }


async def _upload_to_qiniu(data: bytes, file_ext: str, folder: str = "") -> dict:
    """
    上传到七牛云存储
    """
    try:
        from app.utils.qiniu_storage import qiniu_storage
        
        # 直接调用七牛云上传（已经是同步方法，在这里包装为异步）
        result = qiniu_storage.upload_data(data, file_ext, folder)
        return result
        
    except Exception as e:
        print(f"七牛云上传失败: {str(e)}")
        return {
            "success": False,
            "url": "",
            "key": "",
            "error": str(e)
        }


def delete_file(key: str) -> bool:
    """
    删除文件（根据配置选择删除方式）
    
    Args:
        key: 文件的存储key或路径
        
    Returns:
        bool: 是否删除成功
    """
    if settings.STORAGE_TYPE == 1:
        # 本地存储删除
        try:
            if os.path.exists(key):
                os.remove(key)
                return True
            return False
        except Exception as e:
            print(f"本地文件删除失败: {str(e)}")
            return False
    elif settings.STORAGE_TYPE == 2:
        # 七牛云删除
        try:
            from app.utils.qiniu_storage import qiniu_storage
            return qiniu_storage.delete_file(key)
        except Exception as e:
            print(f"七牛云文件删除失败: {str(e)}")
            return False
    else:
        return False
