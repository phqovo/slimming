from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PaginationResponse(BaseModel, Generic[T]):
    """统一分页响应模型"""
    total: int  # 总记录数
    page: int  # 当前页码
    page_size: int  # 每页数量
    total_pages: int  # 总页数
    items: List[T]  # 数据列表
    
    class Config:
        from_attributes = True
