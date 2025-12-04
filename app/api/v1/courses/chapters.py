"""
章节管理API路由
"""
from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterOut
from app.controllers.chapter_controller import ChapterController
from app.core.dependency import DependAuth
from app.models import User

router = APIRouter(tags=["章节管理"])


class ChapterReorderItem(BaseModel):
    """章节重排序项"""
    id: int
    order_num: int


class ChapterReorderRequest(BaseModel):
    """章节重排序请求"""
    chapters: List[ChapterReorderItem]


@router.get("/", response_model=List[ChapterOut], summary="获取章节列表")
async def get_chapters(
    course_id: int = Query(..., description="课程ID"),
    current_user: User = DependAuth
):
    """获取指定课程的章节列表"""
    return await ChapterController.get_chapters_by_course(course_id)


@router.get("/{chapter_id}", response_model=ChapterOut, summary="获取章节详情")
async def get_chapter(
    chapter_id: int,
    current_user: User = DependAuth
):
    """获取章节详情"""
    return await ChapterController.get_chapter(chapter_id)


@router.post("/", response_model=ChapterOut, summary="创建章节")
async def create_chapter(
    chapter_data: ChapterCreate,
    current_user: User = DependAuth
):
    """创建章节"""
    return await ChapterController.create_chapter(chapter_data)


@router.put("/{chapter_id}", response_model=ChapterOut, summary="更新章节")
async def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    current_user: User = DependAuth
):
    """更新章节"""
    return await ChapterController.update_chapter(chapter_id, chapter_data)


@router.delete("/{chapter_id}", summary="删除章节")
async def delete_chapter(
    chapter_id: int,
    current_user: User = DependAuth
):
    """删除章节"""
    await ChapterController.delete_chapter(chapter_id)
    return {"message": "章节删除成功"}


@router.post("/reorder", summary="重新排序章节")
async def reorder_chapters(
    request: ChapterReorderRequest,
    current_user: User = DependAuth
):
    """批量更新章节顺序"""
    chapters_data = [{"id": item.id, "order_num": item.order_num} for item in request.chapters]
    return await ChapterController.reorder_chapters(chapters_data)
