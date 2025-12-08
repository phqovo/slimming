from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.diet import DietRecord
from app.schemas.diet import DietRecordCreate, DietRecordUpdate, DietRecordResponse
from app.api.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

# 导入历史记录重算函数
def trigger_daily_history_recalculate(db: Session, user_id: int, record_date: date):
    """触发历史数据重算"""
    from app.api.v1.weight import trigger_daily_history_recalculate as recalculate
    recalculate(db, user_id, record_date)


@router.post("/", response_model=DietRecordResponse, summary="创建饮食记录")
async def create_diet_record(
    record: DietRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的饮食记录"""
    db_record = DietRecord(
        user_id=current_user.id,
        **record.dict()
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return DietRecordResponse.from_orm(db_record).dict()


@router.get("/", response_model=List[DietRecordResponse], summary="获取饮食记录列表")
async def get_diet_records(
    skip: int = 0,
    limit: int = 100,
    record_date: date = None,
    meal_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的饮食记录列表"""
    query = db.query(DietRecord).filter(DietRecord.user_id == current_user.id)
    
    if record_date:
        query = query.filter(DietRecord.record_date == record_date)
    
    if meal_type:
        query = query.filter(DietRecord.meal_type == meal_type)
    
    records = query.order_by(DietRecord.record_date.desc()).offset(skip).limit(limit).all()
    
    return [DietRecordResponse.from_orm(r).dict() for r in records]


@router.put("/{record_id}", response_model=DietRecordResponse, summary="更新饮食记录")
async def update_diet_record(
    record_id: int,
    record_update: DietRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新饮食记录"""
    record = db.query(DietRecord).filter(
        DietRecord.id == record_id,
        DietRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record.record_date)
    
    return DietRecordResponse.from_orm(record).dict()


@router.delete("/{record_id}", summary="删除饮食记录")
async def delete_diet_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除饮食记录"""
    record = db.query(DietRecord).filter(
        DietRecord.id == record_id,
        DietRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    
    record_date = record.record_date  # 保存日期，删除后重算使用
    
    db.delete(record)
    db.commit()
    
    # 触发历史记录重算
    trigger_daily_history_recalculate(db, current_user.id, record_date)
    
    return {"code": 200, "message": "删除成功"}
