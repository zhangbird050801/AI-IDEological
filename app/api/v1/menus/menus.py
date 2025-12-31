import logging
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException

from app.controllers.menu import menu_controller
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.menus import *

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list", summary="查看菜单列表")
async def list_menu(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    include_deleted: bool = Query(False, description="是否包含已删除的菜单"),
):
    async def get_menu_with_children(menu_id: int, include_deleted: bool = False):
        menu = await menu_controller.model.get(id=menu_id)
        menu_dict = await menu.to_dict()
        
        # 根据参数决定是否包含已删除的子菜单
        if include_deleted:
            child_menus = await menu_controller.model.filter(parent_id=menu_id).order_by("order")
        else:
            child_menus = await menu_controller.model.filter(parent_id=menu_id, is_deleted=False).order_by("order")
        
        menu_dict["children"] = [await get_menu_with_children(child.id, include_deleted) for child in child_menus]
        return menu_dict

    # 根据参数决定是否包含已删除的菜单
    if include_deleted:
        parent_menus = await menu_controller.model.filter(parent_id=0).order_by("order")
    else:
        parent_menus = await menu_controller.model.filter(parent_id=0, is_deleted=False).order_by("order")
    
    res_menu = [await get_menu_with_children(menu.id, include_deleted) for menu in parent_menus]
    return SuccessExtra(data=res_menu, total=len(res_menu), page=page, page_size=page_size)


@router.get("/get", summary="查看菜单")
async def get_menu(
    menu_id: int = Query(..., description="菜单id"),
):
    result = await menu_controller.get(id=menu_id)
    return Success(data=result)


@router.post("/create", summary="创建菜单")
async def create_menu(
    menu_in: MenuCreate,
):
    await menu_controller.create(obj_in=menu_in)
    return Success(msg="Created Success")


@router.post("/update", summary="更新菜单")
async def update_menu(
    menu_in: MenuUpdate,
):
    await menu_controller.update(id=menu_in.id, obj_in=menu_in)
    return Success(msg="Updated Success")


@router.delete("/delete", summary="删除菜单（物理删除）")
async def delete_menu(
    id: int = Query(..., description="菜单id"),
):
    child_menu_count = await menu_controller.model.filter(parent_id=id, is_deleted=False).count()
    if child_menu_count > 0:
        return Fail(msg="Cannot delete a menu with child menus")
    await menu_controller.remove(id=id)
    return Success(msg="Deleted Success")


@router.post("/soft-delete", summary="软删除菜单（移至回收站）")
async def soft_delete_menu(
    id: int = Query(..., description="菜单id"),
):
    """将菜单移至回收站（软删除）"""
    menu = await menu_controller.model.get_or_none(id=id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # 检查是否有未删除的子菜单
    child_menu_count = await menu_controller.model.filter(parent_id=id, is_deleted=False).count()
    if child_menu_count > 0:
        return Fail(msg="无法删除含有子菜单的菜单，请先删除子菜单")
    
    # 软删除
    menu.is_deleted = True
    menu.deleted_at = datetime.now()
    await menu.save()
    
    return Success(msg="菜单已移至回收站")


@router.get("/recycle-bin", summary="获取回收站菜单列表")
async def get_recycle_bin(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """获取所有已删除的菜单"""
    deleted_menus = await menu_controller.model.filter(is_deleted=True).order_by("-deleted_at")
    
    menu_list = []
    for menu in deleted_menus:
        menu_dict = await menu.to_dict()
        menu_list.append(menu_dict)
    
    total = len(menu_list)
    start = (page - 1) * page_size
    end = start + page_size
    
    return SuccessExtra(data=menu_list[start:end], total=total, page=page, page_size=page_size)


@router.post("/restore", summary="从回收站恢复菜单")
async def restore_menu(
    id: int = Query(..., description="菜单id"),
):
    """从回收站恢复菜单"""
    menu = await menu_controller.model.get_or_none(id=id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    if not menu.is_deleted:
        return Fail(msg="该菜单未被删除")
    
    # 检查父菜单是否存在且未被删除
    if menu.parent_id > 0:
        parent_menu = await menu_controller.model.get_or_none(id=menu.parent_id)
        if not parent_menu or parent_menu.is_deleted:
            return Fail(msg="父菜单不存在或已被删除，请先恢复父菜单")
    
    # 恢夏菜单
    menu.is_deleted = False
    menu.deleted_at = None
    await menu.save()
    
    return Success(msg="菜单已恢复")


@router.post("/update-order", summary="更新菜单排序")
async def update_menu_order(
    menu_id: int = Query(..., description="菜单ID"),
    new_order: int = Query(..., description="新排序值"),
    new_parent_id: int = Query(None, description="新父菜单ID（可选）"),
):
    """更新菜单的排序值和父菜单"""
    menu = await menu_controller.model.get_or_none(id=menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # 更新排序
    menu.order = new_order
    
    # 如果提供了新父菜单ID，则更新父菜单
    if new_parent_id is not None:
        menu.parent_id = new_parent_id
    
    await menu.save()
    
    return Success(msg="排序更新成功")


@router.post("/batch-update-order", summary="批量更新菜单排序")
async def batch_update_menu_order(
    orders: list = Query(..., description="菜单排序列表 [{id: 1, order: 1}, ...]"),
):
    """批量更新菜单排序"""
    for item in orders:
        menu = await menu_controller.model.get_or_none(id=item['id'])
        if menu:
            menu.order = item['order']
            if 'parent_id' in item:
                menu.parent_id = item['parent_id']
            await menu.save()
    
    return Success(msg="批量排序更新成功")


@router.delete("/permanent-delete", summary="永久删除菜单（从回收站彻底删除）")
async def permanent_delete_menu(
    id: int = Query(..., description="菜单id"),
):
    """从回收站永久删除菜单"""
    menu = await menu_controller.model.get_or_none(id=id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    if not menu.is_deleted:
        return Fail(msg="只能永久删除已在回收站中的菜单")
    
    await menu_controller.remove(id=id)
    return Success(msg="菜单已永久删除")


@router.post("/empty-recycle-bin", summary="清空回收站")
async def empty_recycle_bin():
    """清空回收站中的所有菜单"""
    deleted_menus = await menu_controller.model.filter(is_deleted=True)
    for menu in deleted_menus:
        await menu.delete()
    
    return Success(msg=f"已清空回收站，删除了 {len(deleted_menus)} 个菜单")
