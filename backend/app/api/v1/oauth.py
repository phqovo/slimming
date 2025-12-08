"""OAuth登录接口（微信、QQ）"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import httpx
import uuid
import hashlib
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import create_access_token
from app.core.config import get_settings
from app.models.user import User
from app.utils.oauth_helper import process_oauth_user_info

router = APIRouter()

# 获取配置（使用依赖注入）
def get_oauth_config():
    settings = get_settings()
    return {
        'WECHAT_APP_ID': settings.WECHAT_APP_ID,
        'WECHAT_APP_SECRET': settings.WECHAT_APP_SECRET,
        'WECHAT_REDIRECT_URI': "https://piheqi.com/health/api/v1/oauth/wechat/callback",
        'QQ_APP_ID': settings.QQ_APP_ID,
        'QQ_APP_KEY': settings.QQ_APP_KEY,
        'QQ_REDIRECT_URI': "https://piheqi.com/health/api/v1/oauth/qq/callback"
    }


@router.get("/wechat/login-url", summary="获取微信登录URL")
async def get_wechat_login_url():
    """生成微信扫码登录URL"""
    config = get_oauth_config()
    state = str(uuid.uuid4())  # 防CSRF攻击
    
    # 构建微信登录URL
    login_url = (
        f"https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={config['WECHAT_APP_ID']}"
        f"&redirect_uri={config['WECHAT_REDIRECT_URI']}"
        f"&response_type=code"
        f"&scope=snsapi_login"
        f"&state={state}"
        f"#wechat_redirect"
    )
    
    return {
        "login_url": login_url,
        "state": state
    }


@router.get("/wechat/callback", summary="微信登录/绑定回调")
async def wechat_callback(
    code: str = Query(..., description="微信授权code"),
    state: str = Query(..., description="state参数"),
    user_agent: str = Header(None),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """
    微信登录/绑定回调处理
    如果state以bind_开头，则调用绑定逻辑
    否则执行登录逻辑
    """
    # 检查是否为绑定请求
    if state.startswith("bind_"):
        # 转发到绑定处理
        from app.api.v1.account_bind import wechat_bind_callback
        return await wechat_bind_callback(code, state, db, redis_client)
    
    # 以下是登录逻辑
    config = get_oauth_config()
    try:
        # 1. 用code换取access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.get(
                "https://api.weixin.qq.com/sns/oauth2/access_token",
                params={
                    "appid": config['WECHAT_APP_ID'],
                    "secret": config['WECHAT_APP_SECRET'],
                    "code": code,
                    "grant_type": "authorization_code"
                }
            )
            token_data = token_response.json()
            
            if "errcode" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信授权失败: {token_data.get('errmsg')}"
                )
            
            access_token = token_data.get("access_token")
            openid = token_data.get("openid")
            unionid = token_data.get("unionid")
            
            # 2. 获取用户信息
            user_response = await client.get(
                "https://api.weixin.qq.com/sns/userinfo",
                params={
                    "access_token": access_token,
                    "openid": openid
                }
            )
            user_data = user_response.json()
            
            if "errcode" in user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"获取用户信息失败: {user_data.get('errmsg')}"
                )
        
        # 3. 处理用户信息
        user_info = process_oauth_user_info(
            nickname=user_data.get("nickname"),
            avatar_url=user_data.get("headimgurl"),
            platform="wechat"
        )
        
        # 4. 查找或创建用户
        user = db.query(User).filter(User.wechat_openid == openid).first()
        
        if not user:
            # 新用户，创建账号
            user = User(
                wechat_openid=openid,
                wechat_unionid=unionid,
                nickname=user_info['nickname'],
                avatar=user_info['avatar'],
                oauth_avatar=user_info['oauth_avatar'],
                gender="male" if user_data.get("sex") == 1 else "female" if user_data.get("sex") == 2 else ""
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 5. 生成JWT token并保存到Redis
        # OAuth登录使用微信openid作为device_id的一部分（保证唯一性）
        device_id = f"wechat_{openid[:16]}"
        
        # 生成Token（将device_id也存入token payload）
        settings = get_settings()
        token_data = {"user_id": user.id, "device_id": device_id}
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # 调试日志
        print(f"\n=== 微信登录成功 ===")
        print(f"用户ID: {user.id}")
        print(f"OpenID: {openid}")
        print(f"Device ID: {device_id}")
        print(f"Token: {token[:50]}...")
        print(f"Redis Key: token:{user.id}:{device_id}")
        
        # 将token存储到Redis
        redis_client.setex(
            f"token:{user.id}:{device_id}",
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            token
        )
        
        print(f"Token已保存到Redis")
        print(f"===================\n")
        
        # 重定向到前端页面（不使用hash路由）
        return RedirectResponse(url=f"https://piheqi.com/health/login-success?token={token}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"微信登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.get("/qq/login-url", summary="获取QQ登录URL")
async def get_qq_login_url():
    """生成QQ扫码登录URL"""
    config = get_oauth_config()
    state = str(uuid.uuid4())
    
    login_url = (
        f"https://graph.qq.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={config['QQ_APP_ID']}"
        f"&redirect_uri={config['QQ_REDIRECT_URI']}"
        f"&state={state}"
        f"&scope=get_user_info"
    )
    
    return {
        "login_url": login_url,
        "state": state
    }


@router.get("/qq/callback", summary="QQ登录/绑定回调")
async def qq_callback(
    code: str = Query(..., description="QQ授权code"),
    state: str = Query(..., description="state参数"),
    user_agent: str = Header(None),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """QQ登录/绑定回调处理"""
    
    # 检查是否为绑定请求
    if state.startswith("bind_"):
        # 转发到绑定处理
        from app.api.v1.account_bind import qq_bind_callback
        return await qq_bind_callback(code, state, db, redis_client)
    
    # 以下是QQ登录逻辑
    config = get_oauth_config()
    
    print(f"\n=== QQ登录回调开始 ===")
    print(f"Code: {code}")
    print(f"State: {state}")
    
    try:
        # 1. 用code换取access_token
        async with httpx.AsyncClient() as client:
            print("\n步骤1: 获取access_token")
            token_response = await client.get(
                "https://graph.qq.com/oauth2.0/token",
                params={
                    "grant_type": "authorization_code",
                    "client_id": config['QQ_APP_ID'],
                    "client_secret": config['QQ_APP_KEY'],
                    "code": code,
                    "redirect_uri": config['QQ_REDIRECT_URI']
                }
            )
            # QQ返回的是URL编码格式，需要解析
            token_text = token_response.text
            print(f"Token响应: {token_text}")
            
            import urllib.parse
            token_params = urllib.parse.parse_qs(token_text)
            
            if "error" in token_params:
                error_msg = f"QQ授权失败: {token_params.get('error_description', ['未知错误'])[0]}"
                print(f"❌ {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            access_token = token_params.get("access_token", [""])[0]
            print(f"✅ Access Token获取成功: {access_token[:20]}...")
            
            # 2. 获取OpenID
            print("\n步骤2: 获取OpenID")
            openid_response = await client.get(
                "https://graph.qq.com/oauth2.0/me",
                params={"access_token": access_token}
            )
            openid_text = openid_response.text
            print(f"OpenID响应: {openid_text}")
            
            # 返回格式：callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
            import json
            import re
            match = re.search(r'callback\(\s*(\{.*?\})\s*\)', openid_text)
            if match:
                openid_data = json.loads(match.group(1))
                openid = openid_data.get("openid")
                print(f"✅ OpenID获取成功: {openid}")
            else:
                print(f"❌ OpenID解析失败")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取OpenID失败"
                )
            
            # 3. 获取用户信息
            print("\n步骤3: 获取用户信息")
            user_response = await client.get(
                "https://graph.qq.com/user/get_user_info",
                params={
                    "access_token": access_token,
                    "oauth_consumer_key": config['QQ_APP_ID'],
                    "openid": openid
                }
            )
            user_data = user_response.json()
            print(f"用户信息响应: {user_data}")
            
            if user_data.get("ret") != 0:
                error_msg = f"获取用户信息失败: {user_data.get('msg')}"
                print(f"❌ {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
        
        # 4. 处理用户信息
        user_info = process_oauth_user_info(
            nickname=user_data.get("nickname"),
            avatar_url=user_data.get("figureurl_qq_2") or user_data.get("figureurl_qq_1"),  # 优先100x100头像
            platform="qq"
        )
        
        # 5. 查找或创建用户
        user = db.query(User).filter(User.qq_openid == openid).first()
        
        if not user:
            user = User(
                qq_openid=openid,
                nickname=user_info['nickname'],
                avatar=user_info['avatar'],
                oauth_avatar=user_info['oauth_avatar'],
                gender="male" if user_data.get("gender") == "男" else "female" if user_data.get("gender") == "女" else ""
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 6. 生成JWT token并保存到Redis
        # OAuth登录使用QQ openid作为device_id的一部分（保证唯一性）
        device_id = f"qq_{openid[:16]}"
        
        # 生成Token（将device_id也存入token payload）
        settings = get_settings()
        token_data = {"user_id": user.id, "device_id": device_id}
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # 调试日志
        print(f"\n=== QQ登录成功 ===")
        print(f"用户ID: {user.id}")
        print(f"OpenID: {openid}")
        print(f"Device ID: {device_id}")
        print(f"Token: {token[:50]}...")
        print(f"Redis Key: token:{user.id}:{device_id}")
        
        # 将token存储到Redis
        redis_client.setex(
            f"token:{user.id}:{device_id}",
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            token
        )
        
        print(f"Token已保存到Redis")
        print(f"===================\n")
        
        # 重定向到前端页面（不使用hash路由）
        return RedirectResponse(url=f"https://piheqi.com/health/login-success?token={token}")
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n\n=== QQ登录异常 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"详细堆栈:\n{error_detail}")
        print(f"===================\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {type(e).__name__}: {str(e) or '未知错误'}"
        )
