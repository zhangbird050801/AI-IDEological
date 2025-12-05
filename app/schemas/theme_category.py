from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ThemeCategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    order: int = Field(default=0, description="排序")
    is_active: bool = Field(default=True, description="是否启用")


class ThemeCategoryCreate(ThemeCategoryBase):
    pass


class ThemeCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ThemeCategoryInDB(ThemeCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ThemeCategory(ThemeCategoryInDB):
    pass


class ThemeCategoryTree(ThemeCategory):
    """分类树节点（包含子节点）"""
    children: List['ThemeCategoryTree'] = Field(default_factory=list, description="子分类列表")

    class Config:
        from_attributes = True


# 更新前向引用
ThemeCategoryTree.model_rebuild()
