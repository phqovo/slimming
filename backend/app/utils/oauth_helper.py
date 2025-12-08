"""OAuth登录工具函数"""
import random
import hashlib
import requests
from typing import Optional


def generate_default_nickname(platform: str = "") -> str:
    """
    生成默认昵称
    
    :param platform: 平台名称 'wechat' | 'qq'
    :return: 默认昵称
    """
    prefixes = ['健康', '活力', '阳光', '快乐', '运动', '元气']
    suffixes = ['达人', '小天使', '追梦人', '健身者', '爱好者', '用户']
    random_num = random.randint(1000, 9999)
    
    return f"{random.choice(prefixes)}{random.choice(suffixes)}{random_num}"


def get_default_avatar() -> str:
    """
    获取系统默认头像URL
    
    :return: 默认头像URL
    """
    # 可以准备多个默认头像，随机返回一个
    default_avatars = [
        '/static/avatars/default_avatar.png',
    ]
    return random.choice(default_avatars)


def download_and_save_avatar(avatar_url: str) -> Optional[str]:
    """
    下载第三方头像并保存到本地/云存储
    
    :param avatar_url: 第三方头像URL
    :return: 保存后的URL，失败则返回None
    """
    if not avatar_url:
        return None
    
    try:
        # 1. 下载头像
        response = requests.get(avatar_url, timeout=10, verify=False)
        if response.status_code != 200:
            print(f"下载头像失败，状态码: {response.status_code}")
            return None
        
        # 2. 生成文件名（基于URL的hash避免重复下载）
        url_hash = hashlib.md5(avatar_url.encode()).hexdigest()
        filename = f"avatars/oauth/{url_hash}.jpg"
        
        # TODO: 这里可以集成七牛云上传
        # from app.utils.qiniu_storage import upload_to_qiniu
        # qiniu_url = upload_to_qiniu(response.content, filename)
        # return qiniu_url
        
        # 暂时返回原URL（后续可改为本地存储或云存储）
        return avatar_url
        
    except Exception as e:
        print(f"下载头像异常: {e}")
        return None


def process_oauth_user_info(
    nickname: Optional[str], 
    avatar_url: Optional[str],
    platform: str = ""
) -> dict:
    """
    处理第三方登录的用户信息
    
    :param nickname: 第三方昵称
    :param avatar_url: 第三方头像URL
    :param platform: 平台名称
    :return: 处理后的用户信息字典
    """
    # 处理昵称
    final_nickname = nickname.strip() if nickname else generate_default_nickname(platform)
    if not final_nickname:
        final_nickname = generate_default_nickname(platform)
    
    # 处理头像
    final_avatar = download_and_save_avatar(avatar_url)
    if not final_avatar:
        final_avatar = get_default_avatar()
    
    return {
        'nickname': final_nickname,
        'avatar': final_avatar,
        'oauth_avatar': avatar_url  # 保存原始URL
    }
