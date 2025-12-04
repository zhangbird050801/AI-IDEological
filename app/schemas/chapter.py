"""
章节相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChapterBase(BaseModel):
    """章节基础模型"""
    course_id: int = Field(..., description="课程ID")
    parent_id: int = Field(0, description="父章节ID")
    name: str = Field(..., max_length=200, description="章节名称")
    description: Optional[str] = Field(None, description="章节描述")
    order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否启用")


class ChapterCreate(ChapterBase):
    """创建章节"""
    pass


class ChapterUpdate(BaseModel):
    """更新章节"""
    parent_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class ChapterOut(ChapterBase):
    """章节输出"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterTree(ChapterOut):
    """章节树形结构"""
    children: List['ChapterTree'] = []
