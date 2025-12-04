"""
案例分类管理API路由
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from app.schemas.case_category import CaseCategoryCreate, CaseCategoryUpdate, CaseCategoryOut, CaseCategoryTree
from app.controllers.case_category_controller import CaseCategoryController
from app.core.dependency import DependAuth
from app.models import User

router = APIRouter(tags=["案例分类管理"])


class CategoryMoveRequest(BaseModel):
    """分类移动请求"""
    parent_id: int = None
    order_num: int = 0


@router.get("/tree", response_model=List[CaseCategoryTree], summary="获取分类树")
async def get_category_tree(
    current_user: User = DependAuth
):
    """获取完整的分类树结构"""
    return await CaseCategoryController.get_category_tree()


@router.get("/", response_model=List[CaseCategoryOut], summary="获取分类列表")
async def get_categories(
    current_user: User = DependAuth
):
    """获取所有分类（扁平列表）"""
    return await CaseCategoryController.get_all_categories()


@router.get("/{category_id}", response_model=CaseCategoryOut, summary="获取分类详情")
async def get_category(
    category_id: int,
    current_user: User = DependAuth
):
    """获取分类详情"""
    return await CaseCategoryController.get_category(category_id)


@router.post("/", response_model=CaseCategoryOut, summary="创建分类")
async def create_category(
    category_data: CaseCategoryCreate,
    current_user: User = DependAuth
):
    """创建分类"""
    return await CaseCategoryController.create_category(category_data)


@router.put("/{category_id}", response_model=CaseCategoryOut, summary="更新分类")
async def update_category(
    category_id: int,
    category_data: CaseCategoryUpdate,
    current_user: User = DependAuth
):
    """更新分类"""
    return await CaseCategoryController.update_category(category_id, category_data)


@router.delete("/{category_id}", summary="删除分类")
async def delete_category(
    category_id: int,
    current_user: User = DependAuth
):
    """删除分类"""
    await CaseCategoryController.delete_category(category_id)
    return {"message": "分类删除成功"}


@router.post("/{category_id}/move", response_model=CaseCategoryOut, summary="移动分类")
async def move_category(
    category_id: int,
    move_data: CategoryMoveRequest,
    current_user: User = DependAuth
):
    """移动分类到新的父分类下"""
    return await CaseCategoryController.move_category(
        category_id, 
        move_data.parent_id, 
        move_data.order_num
    )
