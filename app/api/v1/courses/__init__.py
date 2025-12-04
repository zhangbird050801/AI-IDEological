"""
课程管理API
"""
from fastapi import APIRouter
from .courses import router as courses_router
from .chapters import router as chapters_router
from .knowledge_points import router as knowledge_points_router

router = APIRouter()
router.include_router(courses_router, prefix="/courses")
router.include_router(chapters_router, prefix="/chapters")
router.include_router(knowledge_points_router, prefix="/knowledge-points")
