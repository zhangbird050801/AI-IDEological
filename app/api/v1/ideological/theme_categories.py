from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.controllers.theme_category_controller import theme_category_controller
from app.schemas.theme_category import (
    ThemeCategoryCreate,
    ThemeCategoryUpdate,
    ThemeCategory,
    ThemeCategoryTree
)
from app.schemas.base import Success
from app.models.admin import User
from app.models.ideological import IdeologicalCase
from app.core.dependency import AuthControl

router = APIRouter()


@router.get("/tree", summary="获取分类树", response_model=List[ThemeCategoryTree])
async def get_category_tree(
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取思政主题分类树"""
    return await theme_category_controller.get_tree()


@router.get("/list", summary="获取分类列表", response_model=List[ThemeCategory])
async def get_categories(
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取所有分类（扁平列表）"""
    return await theme_category_controller.get_all()


@router.get("/names", summary="获取主题名称列表")
async def get_theme_names(
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取所有启用的主题名称列表（用于选择器），只返回二级分类"""
    categories = await theme_category_controller.get_all()
    # 只返回启用的二级分类（有parent_id的）主题名称
    names = [cat.name for cat in categories if cat.is_active and cat.parent_id is not None]
    return names


@router.get("/{category_id}", summary="获取分类详情", response_model=ThemeCategory)
async def get_category(
    category_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """根据ID获取分类"""
    category = await theme_category_controller.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.post("", summary="创建分类", response_model=ThemeCategory)
async def create_category(
    category_in: ThemeCategoryCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    """创建新分类"""
    try:
        return await theme_category_controller.create(category_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}", summary="更新分类", response_model=ThemeCategory)
async def update_category(
    category_id: int,
    category_in: ThemeCategoryUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    """更新分类"""
    try:
        return await theme_category_controller.update(category_id, category_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", summary="删除分类")
async def delete_category(
    category_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """删除分类"""
    try:
        await theme_category_controller.delete(category_id)
        return Success(msg="删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{category_id}/move", summary="移动分类")
async def move_category(
    category_id: int,
    parent_id: Optional[int] = None,
    order: int = 0,
    current_user: User = Depends(AuthControl.is_authed)
):
    """移动分类（拖拽排序）"""
    try:
        return await theme_category_controller.move(category_id, parent_id, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/case-count", summary="获取各分类的案例数量统计")
async def get_case_count_stats(
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取每个主题分类关联的案例数量（根分类包含子分类）"""
    from app.models.theme_category import IdeologicalThemeCategory
    categories = await theme_category_controller.get_all()
    
    # 统计每个分类的案例数量
    stats = {}
    for category in categories:
        # 如果是根分类，统计自身和所有子分类的案例
        if category.parent_id is None:
            # 获取所有子分类
            children = await IdeologicalThemeCategory.filter(parent_id=category.id)
            category_ids = [category.id] + [child.id for child in children]
            count = await IdeologicalCase.filter(theme_category_id__in=category_ids).count()
        else:
            # 子分类只统计自身
            count = await IdeologicalCase.filter(theme_category_id=category.id).count()
        
        stats[category.id] = count
    
    return stats


@router.get("/{category_id}/cases", summary="获取某个分类的所有案例")
async def get_category_cases(
    category_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取指定分类下的所有案例（包括子分类）"""
    category = await theme_category_controller.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 获取当前分类及其所有子分类的ID
    category_ids = [category_id]
    
    # 如果是根分类（parent_id为null），要包括所有子分类
    if category.parent_id is None:
        from app.models.theme_category import IdeologicalThemeCategory
        children = await IdeologicalThemeCategory.filter(parent_id=category_id)
        category_ids.extend([child.id for child in children])
    
    # 查询所有相关分类的案例
    cases = await IdeologicalCase.filter(theme_category_id__in=category_ids).prefetch_related('author')
    
    return {
        "category": category,
        "cases": [
            {
                "id": case.id,
                "title": case.title,
                "content": case.content[:200] + "..." if len(case.content) > 200 else case.content,
                "software_engineering_chapter": case.software_engineering_chapter,
                "case_type": case.case_type,
                "difficulty_level": case.difficulty_level,
                "rating": case.rating,
                "usage_count": case.usage_count,
                "is_public": case.is_public,
                "created_at": case.created_at,
                "author_id": case.author_id,
            }
            for case in cases
        ],
        "total": len(cases),
        "included_categories": category_ids  # 返回包含的分类ID列表
    }
