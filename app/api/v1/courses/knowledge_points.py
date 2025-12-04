"""
知识点管理API路由
"""
from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel
from app.schemas.knowledge_point import KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointOut
from app.controllers.knowledge_point_controller import KnowledgePointController
from app.core.dependency import DependAuth
from app.models import User

router = APIRouter(tags=["知识点管理"])


class KnowledgePointReorderItem(BaseModel):
    """知识点重排序项"""
    id: int
    order: int


class KnowledgePointReorderRequest(BaseModel):
    """知识点重排序请求"""
    knowledge_points: List[KnowledgePointReorderItem]


@router.get("/", response_model=List[KnowledgePointOut], summary="获取知识点列表")
async def get_knowledge_points(
    chapter_id: int = Query(..., description="章节ID"),
    current_user: User = DependAuth
):
    """获取指定章节的知识点列表"""
    return await KnowledgePointController.get_knowledge_points_by_chapter(chapter_id)


@router.get("/{knowledge_point_id}", response_model=KnowledgePointOut, summary="获取知识点详情")
async def get_knowledge_point(
    knowledge_point_id: int,
    current_user: User = DependAuth
):
    """获取知识点详情"""
    return await KnowledgePointController.get_knowledge_point(knowledge_point_id)


@router.post("/", response_model=KnowledgePointOut, summary="创建知识点")
async def create_knowledge_point(
    knowledge_point_data: KnowledgePointCreate,
    current_user: User = DependAuth
):
    """创建知识点"""
    return await KnowledgePointController.create_knowledge_point(knowledge_point_data)


@router.put("/{knowledge_point_id}", response_model=KnowledgePointOut, summary="更新知识点")
async def update_knowledge_point(
    knowledge_point_id: int,
    knowledge_point_data: KnowledgePointUpdate,
    current_user: User = DependAuth
):
    """更新知识点"""
    return await KnowledgePointController.update_knowledge_point(knowledge_point_id, knowledge_point_data)


@router.delete("/{knowledge_point_id}", summary="删除知识点")
async def delete_knowledge_point(
    knowledge_point_id: int,
    current_user: User = DependAuth
):
    """删除知识点"""
    await KnowledgePointController.delete_knowledge_point(knowledge_point_id)
    return {"message": "知识点删除成功"}


@router.post("/reorder", summary="重新排序知识点")
async def reorder_knowledge_points(
    request: KnowledgePointReorderRequest,
    current_user: User = DependAuth
):
    """批量更新知识点顺序"""
    knowledge_points_data = [{"id": item.id, "order": item.order} for item in request.knowledge_points]
    return await KnowledgePointController.reorder_knowledge_points(knowledge_points_data)
