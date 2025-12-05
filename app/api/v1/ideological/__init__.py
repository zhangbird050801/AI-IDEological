from fastapi import APIRouter
from .cases import router as cases_router
from .templates import router as templates_router
from .resources import router as resources_router
from .prompt_assistant import router as prompt_assistant_router
from .theme_categories import router as theme_categories_router

router = APIRouter()

# 注册所有子路由
router.include_router(cases_router, prefix="/cases", tags=["案例库管理"])
router.include_router(templates_router, prefix="/templates", tags=["提示词模板管理"])
router.include_router(resources_router, prefix="/resources", tags=["教学资源管理"])
router.include_router(prompt_assistant_router, prefix="/prompt-assistant", tags=["提示词助手"])
router.include_router(theme_categories_router, prefix="/theme-categories", tags=["思政主题分类管理"])

@router.get("/", summary="课程思政内容生成及管理系统API")
async def ideological_info():
    return {
        "name": "课程思政内容生成及管理系统",
        "version": "1.0.0",
        "description": "基于AIGC的《软件工程》课程思政内容生成及管理系统",
        "modules": {
            "cases": "案例库管理",
            "templates": "提示词模板管理",
            "resources": "教学资源管理"
        }
    }