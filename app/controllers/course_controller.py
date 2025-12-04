"""
课程控制器
"""
from typing import Optional, List
from fastapi import HTTPException
from tortoise.expressions import Q
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut


class CourseController:
    """课程控制器"""

    @staticmethod
    async def get_courses(
        page: int = 1,
        size: int = 10,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """获取课程列表（分页）"""
        query = Course.all()

        # 关键词搜索
        if keyword:
            query = query.filter(
                Q(name__icontains=keyword) | Q(code__icontains=keyword) | Q(description__icontains=keyword)
            )

        # 状态筛选
        if is_active is not None:
            query = query.filter(is_active=is_active)

        # 总数
        total = await query.count()

        # 分页
        courses = await query.offset((page - 1) * size).limit(size).order_by("-created_at")

        return {
            "items": [CourseOut.model_validate(course) for course in courses],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    @staticmethod
    async def get_all_courses(is_active: bool = True) -> List[CourseOut]:
        """获取所有课程（不分页）"""
        query = Course.all()
        if is_active:
            query = query.filter(is_active=True)

        courses = await query.order_by("-created_at")
        return [CourseOut.model_validate(course) for course in courses]

    @staticmethod
    async def get_course(course_id: int) -> CourseOut:
        """获取课程详情"""
        course = await Course.filter(id=course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        return CourseOut.model_validate(course)

    @staticmethod
    async def create_course(course_data: CourseCreate, user_id: int) -> CourseOut:
        """创建课程"""
        # 检查课程代码是否已存在
        existing = await Course.filter(code=course_data.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="课程代码已存在")

        course = await Course.create(
            **course_data.model_dump(),
            created_by_id=user_id
        )
        return CourseOut.model_validate(course)

    @staticmethod
    async def update_course(course_id: int, course_data: CourseUpdate) -> CourseOut:
        """更新课程"""
        course = await Course.filter(id=course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 如果更新课程代码，检查是否重复
        if course_data.code and course_data.code != course.code:
            existing = await Course.filter(code=course_data.code).first()
            if existing:
                raise HTTPException(status_code=400, detail="课程代码已存在")

        update_data = course_data.model_dump(exclude_unset=True)
        await course.update_from_dict(update_data).save()
        return CourseOut.model_validate(course)

    @staticmethod
    async def delete_course(course_id: int):
        """删除课程"""
        course = await Course.filter(id=course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        await course.delete()
