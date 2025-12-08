from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.water import WaterRecord
from app.models.sleep import SleepRecord
from app.schemas.other import (
    WaterRecordCreate, WaterRecordResponse,
    SleepRecordCreate, SleepRecordUpdate, SleepRecordResponse
)
from app.api.deps import get_current_user

router = APIRouter()

# 导入历史记录重算函数
def trigger_daily_history_recalculate(db: Session, user_id: int, record_date: date):
    """触发历史数据重算"""
    from app.api.v1.weight import trigger_daily_history_recalculate as recalculate
    recalculate(db, user_id, record_date)


# 饮水记录API
@router.post("/water", response_model=WaterRecordResponse, summary="创建饮水记录")
async def create_water_record(
    record: WaterRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的饮水记录"""
    db_record = WaterRecord(user_id=current_user.id, **record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return WaterRecordResponse.from_orm(db_record).dict()


@router.get("/water", response_model=List[WaterRecordResponse], summary="获取饮水记录")
async def get_water_records(
    skip: int = 0,
    limit: int = 100,
    record_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的饮水记录列表"""
    query = db.query(WaterRecord).filter(WaterRecord.user_id == current_user.id)
    
    if record_date:
        query = query.filter(WaterRecord.record_date == record_date)
    
    records = query.order_by(WaterRecord.record_date.desc()).offset(skip).limit(limit).all()
    return [WaterRecordResponse.from_orm(r).dict() for r in records]


# 睡眠记录API
@router.post("/sleep", response_model=SleepRecordResponse, summary="创建睡眠记录")
async def create_sleep_record(
    record: SleepRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的睡眠记录"""
    db_record = SleepRecord(user_id=current_user.id, **record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return SleepRecordResponse.from_orm(db_record).dict()


@router.get("/sleep", response_model=List[SleepRecordResponse], summary="获取睡眠记录")
async def get_sleep_records(
    skip: int = 0,
    limit: int = 100,
    record_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的睡眠记录列表"""
    query = db.query(SleepRecord).filter(SleepRecord.user_id == current_user.id)
    
    if record_date:
        query = query.filter(SleepRecord.record_date == record_date)
    
    records = query.order_by(SleepRecord.record_date.desc()).offset(skip).limit(limit).all()
    return [SleepRecordResponse.from_orm(r).dict() for r in records]


@router.put("/sleep/{record_id}", response_model=SleepRecordResponse, summary="更新睡眠记录")
async def update_sleep_record(
    record_id: int,
    record_update: SleepRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新睡眠记录"""
    record = db.query(SleepRecord).filter(
        SleepRecord.id == record_id,
        SleepRecord.user_id == current_user.id
    ).first()
    
    if not record:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return SleepRecordResponse.from_orm(record).dict()
