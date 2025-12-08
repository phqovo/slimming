from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.exercise import ExerciseRecord
from app.schemas.exercise import ExerciseRecordCreate, ExerciseRecordUpdate, ExerciseRecordResponse
from app.api.deps import get_current_user
import os
import aiofiles
from datetime import datetime

router = APIRouter()

# 导入历史记录重算函数
def trigger_daily_history_recalculate(db: Session, user_id: int, record_date: date):
    """触发历史数据重算"""
    from app.api.v1.weight import trigger_daily_history_recalculate as recalculate
    recalculate(db, user_id, record_date)


@router.post("/", response_model=ExerciseRecordResponse, summary="创建运动记录")
async def create_exercise_record(
    record: ExerciseRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的运动记录"""
    db_record = ExerciseRecord(
        user_id=current_user.id,
        **record.dict()
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return ExerciseRecordResponse.from_orm(db_record).dict()


@router.get("/", response_model=List[ExerciseRecordResponse], summary="获取运动记录列表")
async def get_exercise_records(
    skip: int = 0,
    limit: int = 100,
    record_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的运动记录列表"""
    query = db.query(ExerciseRecord).filter(ExerciseRecord.user_id == current_user.id)
    
    if record_date:
        query = query.filter(ExerciseRecord.record_date == record_date)
    
    records = query.order_by(ExerciseRecord.record_date.desc()).offset(skip).limit(limit).all()
    
    return [ExerciseRecordResponse.from_orm(r).dict() for r in records]


@router.put("/{record_id}", response_model=ExerciseRecordResponse, summary="更新运动记录")
async def update_exercise_record(
    record_id: int,
    record_update: ExerciseRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新运动记录"""
    record = db.query(ExerciseRecord).filter(
        ExerciseRecord.id == record_id,
        ExerciseRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return ExerciseRecordResponse.from_orm(record).dict()


@router.delete("/{record_id}", summary="删除运动记录")
async def delete_exercise_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除运动记录"""
    record = db.query(ExerciseRecord).filter(
        ExerciseRecord.id == record_id,
        ExerciseRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    
    record_date = record.record_date  # 保存日期
    
    db.delete(record)
    db.commit()
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record_date)
    
    return {"code": 200, "message": "删除成功"}


@router.post("/upload-image", summary="上传运动图片")
async def upload_exercise_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传运动记录图片（支持本地/七牛云）"""
    from app.utils.storage import upload_file
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持上传图片文件")
    
    # 读取文件数据
    file_data = await file.read()
    file_ext = os.path.splitext(file.filename)[1]
    
    # 上传文件（自动根据配置选择存储方式）
    result = await upload_file(file_data, file_ext, folder="exercise/")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {result.get('error', '未知错误')}"
        )
    
    image_url = result["url"]
    
    return {"code": 200, "message": "上传成功", "data": {"image_url": image_url}}
