"""
案例分类相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CaseCategoryBase(BaseModel):
    """案例分类基础模型"""
    parent_id: int = Field(0, description="父分类ID")
    name: str = Field(..., max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    color: Optional[str] = Field(None, max_length=20, description="颜色")
    order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否启用")


class CaseCategoryCreate(CaseCategoryBase):
    """创建案例分类"""
    pass


class CaseCategoryUpdate(BaseModel):
    """更新案例分类"""
    parent_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class CaseCategoryOut(CaseCategoryBase):
    """案例分类输出"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseCategoryTree(CaseCategoryOut):
    """案例分类树形结构"""
    children: List['CaseCategoryTree'] = Field(default_factory=list, description="子分类列表")
    case_count: int = Field(0, description="关联的案例数量")
    level: int = Field(0, description="层级深度")
