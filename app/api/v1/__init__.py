from fastapi import APIRouter

from app.core.dependency import DependPermission

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .depts import depts_router
from .menus import menus_router
from .roles import roles_router
from .users import users_router
from .aigc import chat as aigc_chat
from .aigc import enhanced as aigc_enhanced
from .ideological import router as ideological_router
from .ideological.prompt_assistant import router as prompt_assistant_router

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(users_router, prefix="/user", dependencies=[DependPermission])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DependPermission])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermission])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DependPermission])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermission])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermission])
v1_router.include_router(aigc_chat.router, prefix="/aigc")
v1_router.include_router(aigc_enhanced.router, prefix="/aigc/enhanced", dependencies=[DependPermission])
v1_router.include_router(ideological_router, prefix="/ideological")
v1_router.include_router(prompt_assistant_router, prefix="/ideological/prompt-assistant", dependencies=[DependPermission])
