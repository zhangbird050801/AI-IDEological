import json
import re
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.dependency import AuthControl
from app.models.admin import User

from .bgtask import BgTasks


class SimpleBaseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def before_request(self, request: Request):
        return self.app

    async def after_request(self, request: Request):
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    async def before_request(self, request):
        try:
            await BgTasks.init_bg_tasks_obj()
        except Exception as e:
            print(f"后台任务初始化异常: {e}")

    async def after_request(self, request):
        try:
            await BgTasks.execute_tasks()
        except Exception as e:
            print(f"后台任务执行异常: {e}")


# HttpAuditLogMiddleware 已移除 - 不再需要审计日志功能
