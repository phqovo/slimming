"""账号绑定相关接口"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import httpx
import uuid

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import create_access_token
from app.core.config import get_settings
from app.models.user import User
from app.api.deps import get_current_user
from app.api.v1.oauth import get_oauth_config, process_oauth_user_info
from pydantic import BaseModel

router = APIRouter()


class MergeAccountRequest(BaseModel):
    """账号合并请求"""
    temp_bind_token: str  # 临时绑定token
    action: str  # "merge" 或 "replace"


@router.get("/qq/bind-url", summary="获取QQ绑定URL")
async def get_qq_bind_url(current_user: User = Depends(get_current_user)):
    """生成QQ绑定URL（需要登录）"""
    config = get_oauth_config()
    state = f"bind_{current_user.id}_{uuid.uuid4()}"
    
    # 使用与登录相同的回调地址（通过state区分）
    callback_url = "https://piheqi.com/health/api/v1/oauth/qq/callback"
    
    bind_url = (
        f"https://graph.qq.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={config['QQ_APP_ID']}"
        f"&redirect_uri={callback_url}"
        f"&state={state}"
        f"&scope=get_user_info"
    )
    
    return {
        "bind_url": bind_url,
        "state": state
    }


@router.get("/wechat/bind-url", summary="获取微信绑定URL")
async def get_wechat_bind_url(current_user: User = Depends(get_current_user)):
    """生成微信绑定URL（需要登录）"""
    config = get_oauth_config()
    state = f"bind_{current_user.id}_{uuid.uuid4()}"
    
    # 使用与登录相同的回调地址（通过state区分）
    callback_url = "https://piheqi.com/health/api/v1/oauth/wechat/callback"
    
    bind_url = (
        f"https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={config['WECHAT_APP_ID']}"
        f"&redirect_uri={callback_url}"
        f"&response_type=code"
        f"&scope=snsapi_login"
        f"&state={state}#wechat_redirect"
    )
    
    return {
        "bind_url": bind_url,
        "state": state
    }


@router.get("/qq/bind-callback", summary="QQ绑定回调")
async def qq_bind_callback(
    code: str = Query(..., description="QQ授权code"),
    state: str = Query(..., description="state参数"),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """QQ绑定回调处理"""
    config = get_oauth_config()
    
    print(f"\n=== QQ绑定回调开始 ===")
    print(f"Code: {code}")
    print(f"State: {state}")
    
    # 从state中解析user_id
    if not state.startswith("bind_"):
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败：无效的请求</h2>
                <script>setTimeout(() => window.close(), 2000)</script>
            </body></html>
        """)
    
    try:
        user_id = int(state.split("_")[1])
    except:
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败：无效的用户ID</h2>
                <script>setTimeout(() => window.close(), 2000)</script>
            </body></html>
        """)
    
    # 获取当前用户
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败：用户不存在</h2>
                <script>setTimeout(() => window.close(), 2000)</script>
            </body></html>
        """)
    
    try:
        # 1. 获取QQ的access_token和openid
        async with httpx.AsyncClient() as client:
            print("\n步骤1: 获取access_token")
            
            # 使用与登录相同的回调地址
            callback_url = "https://piheqi.com/health/api/v1/oauth/qq/callback"
            
            token_response = await client.get(
                "https://graph.qq.com/oauth2.0/token",
                params={
                    "grant_type": "authorization_code",
                    "client_id": config['QQ_APP_ID'],
                    "client_secret": config['QQ_APP_KEY'],
                    "code": code,
                    "redirect_uri": callback_url
                }
            )
            
            import urllib.parse
            token_text = token_response.text
            token_params = urllib.parse.parse_qs(token_text)
            
            if "error" in token_params:
                error_msg = token_params.get('error_description', ['未知错误'])[0]
                print(f"❌ {error_msg}")
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定失败：{error_msg}</h2>
                        <script>setTimeout(() => window.close(), 2000)</script>
                    </body></html>
                """)
            
            access_token = token_params.get("access_token", [""])[0]
            print(f"✅ Access Token获取成功")
            
            # 2. 获取OpenID
            print("\n步骤2: 获取OpenID")
            openid_response = await client.get(
                "https://graph.qq.com/oauth2.0/me",
                params={"access_token": access_token}
            )
            openid_text = openid_response.text
            
            import json
            import re
            match = re.search(r'callback\(\s*(\{.*?\})\s*\)', openid_text)
            if match:
                openid_data = json.loads(match.group(1))
                openid = openid_data.get("openid")
                print(f"✅ OpenID获取成功: {openid}")
            else:
                print(f"❌ OpenID解析失败")
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定失败：获取OpenID失败</h2>
                        <script>setTimeout(() => window.close(), 2000)</script>
                    </body></html>
                """)
            
            # 3. 获取QQ用户信息
            print("\n步骤3: 获取QQ用户信息")
            user_info_response = await client.get(
                "https://graph.qq.com/user/get_user_info",
                params={
                    "access_token": access_token,
                    "oauth_consumer_key": config['QQ_APP_ID'],
                    "openid": openid
                }
            )
            user_info = user_info_response.json()
            qq_nickname = user_info.get("nickname", "")
            qq_avatar = user_info.get("figureurl_qq_2") or user_info.get("figureurl_qq_1") or user_info.get("figureurl")
            print(f"✅ QQ用户信息获取成功: {qq_nickname}")
        
        # 4. 检查该QQ是否已被其他用户绑定
        existing_user = db.query(User).filter(User.qq_openid == openid).first()
        
        if existing_user:
            # 该QQ已被其他用户绑定
            if existing_user.phone:
                # 已绑定手机号，不允许绑定
                print(f"❌ 该QQ已绑定手机号的账号，不允许绑定")
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定失败：该QQ号已绑定其他账号</h2>
                        <p>该QQ号已绑定一个有手机号的账号，无法再次绑定</p>
                        <script>setTimeout(() => window.close(), 3000)</script>
                    </body></html>
                """)
            
            # 未绑定手机号，检查是否有数据
            has_data = _check_user_has_data(db, existing_user.id)
            current_has_data = _check_user_has_data(db, current_user.id)
            
            if has_data and current_has_data:
                # 两边都有数据，需要用户选择
                print(f"⚠️ 两个账号都有数据，需要用户选择合并方式")
                
                # 生成临时绑定token
                temp_token = str(uuid.uuid4())
                redis_client.setex(
                    f"temp_bind:{temp_token}",
                    300,  # 5分钟过期
                    json.dumps({
                        "current_user_id": current_user.id,
                        "old_user_id": existing_user.id,
                        "platform": "qq",
                        "openid": openid
                    })
                )
                
                # 重定向到选择页面
                return RedirectResponse(url=f"https://piheqi.com/health/account-merge?token={temp_token}")
            else:
                # 至少有一方没有数据，直接合并
                print(f"✅ 直接合并账号（至少一方无数据）")
                
                # 先合并数据
                _merge_accounts(db, current_user.id, existing_user.id, "merge")
                
                # 删除旧账号的关联数据（外键约束）
                _delete_user_related_data(db, existing_user.id)
                
                # 删除旧账号
                db.delete(existing_user)
                db.commit()
                
                # 更新qq_openid和用户信息
                current_user.qq_openid = openid
                current_user.qq_nickname = qq_nickname
                if qq_avatar and not current_user.oauth_avatar:
                    current_user.oauth_avatar = qq_avatar
                db.commit()
                
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定成功！</h2>
                        <p>已成功绑定QQ号</p>
                        <script>
                            setTimeout(() => {{
                                window.opener && window.opener.postMessage({{type: 'bind_success'}}, '*');
                                window.close();
                            }}, 1500);
                        </script>
                    </body></html>
                """)
        else:
            # 该QQ未被任何用户绑定，直接绑定
            print(f"✅ 直接绑定QQ")
            current_user.qq_openid = openid
            current_user.qq_nickname = qq_nickname
            if qq_avatar and not current_user.oauth_avatar:
                current_user.oauth_avatar = qq_avatar
            db.commit()
            
            return HTMLResponse(content=f"""
                <html><body>
                    <h2>绑定成功！</h2>
                    <p>已成功绑定QQ号</p>
                    <script>
                        setTimeout(() => {{
                            window.opener && window.opener.postMessage({{type: 'bind_success'}}, '*');
                            window.close();
                        }}, 1500);
                    </script>
                </body></html>
            """)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n\n=== QQ绑定异常 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"详细堆栈:\n{error_detail}")
        print(f"===================\n")
        
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败</h2>
                <p>{str(e) or '未知错误'}</p>
                <script>setTimeout(() => window.close(), 3000)</script>
            </body></html>
        """)


@router.post("/merge-account", summary="合并账号")
async def merge_account(
    request: MergeAccountRequest,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """
    合并账号
    action: "merge" - 合并数据, "replace" - 保留当前账号数据
    """
    import json
    
    # 获取临时绑定信息
    bind_info = redis_client.get(f"temp_bind:{request.temp_bind_token}")
    if not bind_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="绑定信息已过期，请重新绑定"
        )
    
    bind_data = json.loads(bind_info)
    current_user_id = bind_data["current_user_id"]
    old_user_id = bind_data["old_user_id"]
    platform = bind_data["platform"]
    openid = bind_data["openid"]
    
    # 获取用户
    current_user = db.query(User).filter(User.id == current_user_id).first()
    old_user = db.query(User).filter(User.id == old_user_id).first()
    
    if not current_user or not old_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 合并或替换数据
    if request.action == "merge":
        _merge_accounts(db, current_user_id, old_user_id, "merge")
    elif request.action == "replace":
        _merge_accounts(db, current_user_id, old_user_id, "replace")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的操作类型"
        )
    
    # 绑定openid
    if platform == "qq":
        current_user.qq_openid = openid
    elif platform == "wechat":
        current_user.wechat_openid = openid
    
    # 删除旧用户
    db.delete(old_user)
    db.commit()
    
    # 删除临时token
    redis_client.delete(f"temp_bind:{request.temp_bind_token}")
    
    return {"message": "账号合并成功"}


@router.get("/wechat/bind-callback", summary="微信绑定回调")
async def wechat_bind_callback(
    code: str = Query(..., description="微信授权code"),
    state: str = Query(..., description="state参数"),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """微信绑定回调处理"""
    config = get_oauth_config()
    
    print(f"\n=== 微信绑定回调开始 ===")
    print(f"Code: {code}")
    print(f"State: {state}")
    
    # 从state中解析user_id
    if not state.startswith("bind_"):
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败：无效的请求</h2>
                <script>setTimeout(() => window.close(), 2000)</script>
            </body></html>
        """)
    
    try:
        user_id = int(state.split("_")[1])
    except:
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败：无效的用户ID</h2>
                <script>setTimeout(() => window.close(), 2000)</script>
            </body></html>
        """)
    
    # 获取当前用户
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败：用户不存在</h2>
                <script>setTimeout(() => window.close(), 2000)</script>
            </body></html>
        """)
    
    try:
        # 1. 获取微信的access_token和openid
        async with httpx.AsyncClient() as client:
            print("\n步骤1: 获取access_token")
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
                error_msg = token_data.get('errmsg', '未知错误')
                print(f"❌ {error_msg}")
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定失败：{error_msg}</h2>
                        <script>setTimeout(() => window.close(), 2000)</script>
                    </body></html>
                """)
            
            openid = token_data.get("openid")
            unionid = token_data.get("unionid")
            print(f"✅ OpenID获取成功: {openid}")
        
        # 2. 检查该微信是否已被其他用户绑定
        existing_user = db.query(User).filter(User.wechat_openid == openid).first()
        
        if existing_user:
            # 该微信已被其他用户绑定
            if existing_user.phone:
                # 已绑定手机号，不允许绑定
                print(f"❌ 该微信已绑定手机号的账号，不允许绑定")
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定失败：该微信号已绑定其他账号</h2>
                        <p>该微信号已绑定一个有手机号的账号，无法再次绑定</p>
                        <script>setTimeout(() => window.close(), 3000)</script>
                    </body></html>
                """)
            
            # 未绑定手机号，检查是否有数据
            has_data = _check_user_has_data(db, existing_user.id)
            current_has_data = _check_user_has_data(db, current_user.id)
            
            if has_data and current_has_data:
                # 两边都有数据，需要用户选择
                print(f"⚠️ 两个账号都有数据，需要用户选择合并方式")
                
                import json
                # 生成临时绑定token
                temp_token = str(uuid.uuid4())
                redis_client.setex(
                    f"temp_bind:{temp_token}",
                    300,  # 5分钟过期
                    json.dumps({
                        "current_user_id": current_user.id,
                        "old_user_id": existing_user.id,
                        "platform": "wechat",
                        "openid": openid,
                        "unionid": unionid
                    })
                )
                
                # 重定向到选择页面
                return RedirectResponse(url=f"https://piheqi.com/health/account-merge?token={temp_token}")
            else:
                # 至少有一方没有数据，直接合并
                print(f"✅ 直接合并账号（至少一方无数据）")
                
                # 先合并数据
                _merge_accounts(db, current_user.id, existing_user.id, "merge")
                
                # 删除旧账号的关联数据（外键约束）
                _delete_user_related_data(db, existing_user.id)
                
                # 删除旧账号
                db.delete(existing_user)
                db.commit()
                
                # 更新微信openid
                current_user.wechat_openid = openid
                current_user.wechat_unionid = unionid
                db.commit()
                
                return HTMLResponse(content=f"""
                    <html><body>
                        <h2>绑定成功！</h2>
                        <p>已成功绑定微信号</p>
                        <script>
                            setTimeout(() => {{
                                window.opener && window.opener.postMessage({{type: 'bind_success'}}, '*');
                                window.close();
                            }}, 1500);
                        </script>
                    </body></html>
                """)
        else:
            # 该微信未被任何用户绑定，直接绑定
            print(f"✅ 直接绑定微信")
            current_user.wechat_openid = openid
            current_user.wechat_unionid = unionid
            db.commit()
            
            return HTMLResponse(content=f"""
                <html><body>
                    <h2>绑定成功！</h2>
                    <p>已成功绑定微信号</p>
                    <script>
                        setTimeout(() => {{
                            window.opener && window.opener.postMessage({{type: 'bind_success'}}, '*');
                            window.close();
                        }}, 1500);
                    </script>
                </body></html>
            """)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n\n=== 微信绑定异常 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"详细堆栈:\n{error_detail}")
        print(f"===================\n")
        
        return HTMLResponse(content=f"""
            <html><body>
                <h2>绑定失败</h2>
                <p>{str(e) or '未知错误'}</p>
                <script>setTimeout(() => window.close(), 3000)</script>
            </body></html>
        """)


def _check_user_has_data(db: Session, user_id: int) -> bool:
    """检查用户是否有数据"""
    from app.models.weight import WeightRecord
    from app.models.exercise import ExerciseRecord
    from app.models.diet import DietRecord
    
    # 检查是否有体重记录
    weight_count = db.query(WeightRecord).filter(WeightRecord.user_id == user_id).count()
    if weight_count > 0:
        return True
    
    # 检查是否有运动记录
    exercise_count = db.query(ExerciseRecord).filter(ExerciseRecord.user_id == user_id).count()
    if exercise_count > 0:
        return True
    
    # 检查是否有饮食记录
    diet_count = db.query(DietRecord).filter(DietRecord.user_id == user_id).count()
    if diet_count > 0:
        return True
    
    return False


def _delete_user_related_data(db: Session, user_id: int):
    """删除用户的所有关联数据（解决外键约束问题）"""
    from app.models.user_settings import UserSettings
    from app.models.sleep import SleepRecord
    from app.models.water import WaterRecord
    
    # 删除用户设置
    db.query(UserSettings).filter(UserSettings.user_id == user_id).delete()
    
    # 删除睡眠记录
    db.query(SleepRecord).filter(SleepRecord.user_id == user_id).delete()
    
    # 删除饮水记录
    db.query(WaterRecord).filter(WaterRecord.user_id == user_id).delete()
    
    db.commit()
    print(f"✅ 已删除用户 {user_id} 的关联数据")


def _merge_accounts(db: Session, keep_user_id: int, remove_user_id: int, action: str):
    """
    合并账号数据
    action: "merge" - 合并数据, "replace" - 保留keep_user的数据
    """
    from app.models.weight import WeightRecord
    from app.models.exercise import ExerciseRecord
    from app.models.diet import DietRecord
    from app.models.daily_history import DailyHistory
    
    if action == "merge":
        # 合并所有数据
        # 1. 合并体重记录
        db.query(WeightRecord).filter(
            WeightRecord.user_id == remove_user_id
        ).update({"user_id": keep_user_id})
        
        # 2. 合并运动记录
        db.query(ExerciseRecord).filter(
            ExerciseRecord.user_id == remove_user_id
        ).update({"user_id": keep_user_id})
        
        # 3. 合并饮食记录
        db.query(DietRecord).filter(
            DietRecord.user_id == remove_user_id
        ).update({"user_id": keep_user_id})
        
        # 4. 合并每日历史记录
        db.query(DailyHistory).filter(
            DailyHistory.user_id == remove_user_id
        ).update({"user_id": keep_user_id})
        
        db.commit()
    elif action == "replace":
        # 删除旧账号的所有数据
        db.query(WeightRecord).filter(WeightRecord.user_id == remove_user_id).delete()
        db.query(ExerciseRecord).filter(ExerciseRecord.user_id == remove_user_id).delete()
        db.query(DietRecord).filter(DietRecord.user_id == remove_user_id).delete()
        db.query(DailyHistory).filter(DailyHistory.user_id == remove_user_id).delete()
        db.commit()
