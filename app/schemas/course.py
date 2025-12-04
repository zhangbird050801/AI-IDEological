"""
课程相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CourseBase(BaseModel):
    """课程基础模型"""
    code: str = Field(..., max_length=50, description="课程代码")
    name: str = Field(..., max_length=200, description="课程名称")
    description: Optional[str] = Field(None, description="课程描述")
    credit: Optional[Decimal] = Field(None, description="学分")
    hours: Optional[int] = Field(None, description="学时")
    semester: Optional[str] = Field(None, max_length=20, description="开课学期")
    is_active: bool = Field(True, description="是否启用")


class CourseCreate(CourseBase):
    """创建课程"""
    pass


class CourseUpdate(BaseModel):
    """更新课程"""
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    credit: Optional[Decimal] = None
    hours: Optional[int] = None
    semester: Optional[str] = None
    is_active: Optional[bool] = None


class CourseOut(CourseBase):
    """课程输出"""
    id: int
    created_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
