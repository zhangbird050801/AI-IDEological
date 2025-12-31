"""
课程管理API路由
"""
from fastapi import APIRouter, Query
from typing import List
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut
from app.controllers.course_controller import CourseController
from app.core.dependency import DependAuth
from app.models import User

router = APIRouter(tags=["基础模块"])


@router.get("/", response_model=dict, summary="获取课程列表")
async def get_courses(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    is_active: bool = Query(None, description="是否启用"),
    current_user: User = DependAuth
):
    """获取课程列表（分页）"""
    return await CourseController.get_courses(
        page=page,
        size=size,
        keyword=keyword,
        is_active=is_active
    )


@router.get("/all", response_model=List[CourseOut], summary="获取所有课程")
async def get_all_courses(
    is_active: bool = Query(True, description="是否只获取启用的课程"),
    current_user: User = DependAuth
):
    """获取所有课程（不分页）"""
    return await CourseController.get_all_courses(is_active=is_active)


@router.get("/{course_id}", response_model=CourseOut, summary="获取课程详情")
async def get_course(
    course_id: int,
    current_user: User = DependAuth
):
    """获取课程详情"""
    return await CourseController.get_course(course_id)


@router.post("/", response_model=CourseOut, summary="创建课程")
async def create_course(
    course_data: CourseCreate,
    current_user: User = DependAuth
):
    """创建课程"""
    return await CourseController.create_course(course_data, current_user.id)


@router.put("/{course_id}", response_model=CourseOut, summary="更新课程")
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = DependAuth
):
    """更新课程"""
    return await CourseController.update_course(course_id, course_data)


@router.delete("/{course_id}", summary="删除课程")
async def delete_course(
    course_id: int,
    current_user: User = DependAuth
):
    """删除课程"""
    await CourseController.delete_course(course_id)
    return {"message": "课程删除成功"}
