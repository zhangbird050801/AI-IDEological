"""
知识点相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KnowledgePointBase(BaseModel):
    """知识点基础模型"""
    chapter_id: int = Field(..., description="章节ID")
    name: str = Field(..., max_length=200, description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    difficulty: int = Field(3, ge=1, le=5, description="难度等级1-5")
    importance: int = Field(3, ge=1, le=5, description="重要程度1-5")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否启用")


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点"""
    pass


class KnowledgePointUpdate(BaseModel):
    """更新知识点"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    importance: Optional[int] = Field(None, ge=1, le=5)
    keywords: Optional[List[str]] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class KnowledgePointOut(KnowledgePointBase):
    """知识点输出"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
