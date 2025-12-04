from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from tortoise.queryset import Q
from tortoise.expressions import F
import os
import uuid
import aiofiles
from pathlib import Path
from app.schemas.ideological import (
    TeachingResourceCreate,
    TeachingResourceUpdate,
    TeachingResource,
    ResourceSearchRequest,
    BatchOperationRequest,
    BatchOperationResponse,
)
from app.models.ideological import TeachingResource as TeachingResourceModel, ResourceType
from app.models.admin import User
from app.core.dependency import AuthControl
from app.core.crud import CRUDBase

router = APIRouter()

# 配置文件上传目录（相对项目根）
UPLOAD_DIR = Path("uploads/teaching_resources")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ResourceService(CRUDBase[TeachingResourceModel, TeachingResourceCreate, TeachingResourceUpdate]):
    def __init__(self):
        super().__init__(TeachingResourceModel)

    async def create_resource(self, obj_in: TeachingResourceCreate, user_id: int, file_path: str = None) -> TeachingResourceModel:
        obj_data = obj_in.dict()
        obj_data["uploader_id"] = user_id
        if file_path:
            obj_data["file_path"] = file_path
        return await self.create(obj_data)

    async def get_resources_with_search(self, search_request: ResourceSearchRequest, user_id: int = None):
        query = TeachingResourceModel.all()

        # 如果不是获取所有公开资源，需要根据用户权限过滤
        if user_id:
            query = query.filter(
                Q(is_public=True) | Q(uploader_id=user_id)
            )
        else:
            query = query.filter(is_public=True)

        # 关键词搜索
        if search_request.keyword:
            keyword = search_request.keyword.strip()
            query = query.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(ideological_theme__icontains=keyword)
            )

        # 其他筛选条件
        if search_request.resource_type:
            query = query.filter(resource_type=search_request.resource_type)

        if search_request.software_engineering_chapter:
            query = query.filter(software_engineering_chapter__icontains=search_request.software_engineering_chapter)

        if search_request.ideological_theme:
            query = query.filter(ideological_theme__icontains=search_request.ideological_theme)

        if search_request.tags:
            for tag in search_request.tags:
                query = query.filter(tags__contains=tag)

        # 排序：按创建时间倒序，按使用次数倒序
        query = query.order_by("-created_at", "-usage_count")

        # 分页
        offset = (search_request.page - 1) * search_request.page_size
        total = await query.count()
        items = await query.offset(offset).limit(search_request.page_size).prefetch_related('uploader')

        return {
            "items": items,
            "total": total,
            "page": search_request.page,
            "page_size": search_request.page_size,
            "pages": (total + search_request.page_size - 1) // search_request.page_size
        }

    async def update_resource_usage(self, resource_id: int):
        resource = await TeachingResourceModel.get_or_none(id=resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="资源不存在")

        await resource.update_from_dict({"usage_count": resource.usage_count + 1})
        await resource.save()

        return resource

    async def get_hot_resources(self, limit: int = 10):
        return await TeachingResourceModel.filter(
            is_public=True
        ).order_by("-usage_count", "-created_at").limit(limit)

    async def upload_file(self, file: UploadFile, user_id: int) -> dict:
        # 验证文件类型
        allowed_extensions = {
            "document": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".flv"],
            "audio": [".mp3", ".wav", ".flac", ".aac"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
            "presentation": [".ppt", ".pptx", ".key"],
            "other": []
        }

        file_extension = Path(file.filename).suffix.lower()

        # 确定文件类型
        resource_type = "other"
        for type_name, extensions in allowed_extensions.items():
            if file_extension in extensions:
                resource_type = type_name
                break

        # 生成唯一文件名
        file_uuid = uuid.uuid4()
        file_name = f"{file_uuid}{file_extension}"
        file_path = UPLOAD_DIR / file_name

        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # 获取文件大小
        file_size = len(content)

        # 构建访问URL
        # 静态可访问的URL（需在 FastAPI 挂载 /uploads）
        static_file_url = f"/uploads/teaching_resources/{file_name}"
        download_url = f"/api/v1/ideological/resources/download/{file_uuid}"

        # 预览URL：图片/PDF/DOCX 直接用静态地址，方便前端内嵌预览
        preview_url = static_file_url if resource_type in ["image", "document"] else None

        return {
            "file_path": str(file_path),
            "file_url": static_file_url,
            "download_url": download_url,
            "preview_url": preview_url,
            "file_size": file_size,
            "file_format": file_extension.lstrip('.'),
            "resource_type": resource_type
        }

resource_service = ResourceService()

@router.get("/", summary="获取教学资源列表")
async def get_resources(
    keyword: str = Query(None, description="关键词搜索"),
    resource_type: str = Query(None, description="资源类型"),
    software_engineering_chapter: str = Query(None, description="软件工程章节"),
    ideological_theme: str = Query(None, description="思政主题"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    search_request = ResourceSearchRequest(
        keyword=keyword,
        resource_type=resource_type,
        software_engineering_chapter=software_engineering_chapter,
        ideological_theme=ideological_theme,
        page=page,
        page_size=page_size
    )

    result = await resource_service.get_resources_with_search(search_request, current_user.id)

    # 转换为响应格式
    resources = [TeachingResource.from_orm(item) for item in result["items"]]

    return {
        "items": resources,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "pages": result["pages"]
    }

@router.post("/", summary="创建教学资源")
async def create_resource(
    title: str = Form(...),
    description: str = Form(None),
    resource_type: str = Form(...),
    external_url: str = Form(None),
    tags: str = Form(None),
    software_engineering_chapter: str = Form(None),
    ideological_theme: str = Form(None),
    is_public: bool = Form(True),
    file: UploadFile = File(None),
    current_user: User = Depends(AuthControl.is_authed)
):
    # 处理文件上传
    file_info = None
    if file and file.filename:
        file_info = await resource_service.upload_file(file, current_user.id)

    # 处理标签
    tags_list = []
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    resource_data = {
        "title": title,
        "description": description,
        "resource_type": resource_type,
        "external_url": external_url,
        "tags": tags_list,
        "software_engineering_chapter": software_engineering_chapter,
        "ideological_theme": ideological_theme,
        "is_public": is_public
    }

    # 如果有上传文件，添加文件相关信息
    if file_info:
        resource_data.update({
            "file_url": file_info["file_url"],
            "file_size": file_info["file_size"],
            "file_format": file_info["file_format"],
            "download_url": file_info["download_url"],
            "preview_url": file_info["preview_url"]
        })

    resource_in = TeachingResourceCreate(**resource_data)
    resource = await resource_service.create_resource(
        resource_in,
        current_user.id,
        file_info["file_path"] if file_info else None
    )

    return TeachingResource.from_orm(resource)


@router.post("/json", summary="创建教学资源（JSON，无文件上传）")
async def create_resource_json(
    resource_in: TeachingResourceCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    """
    允许前端以 JSON 方式创建教学资源（不含文件），避免表单缺少字段导致 422。
    如需上传文件，请使用表单上传接口。
    """
    resource = await resource_service.create_resource(resource_in, current_user.id)
    return TeachingResource.from_orm(resource)

@router.get("/{resource_id}", summary="获取教学资源详情")
async def get_resource(
    resource_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    resource = await TeachingResourceModel.get_or_none(id=resource_id).prefetch_related('uploader')
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 检查权限
    if not resource.is_public and resource.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该资源")

    # 增加使用次数
    await resource_service.update_resource_usage(resource_id)

    return TeachingResource.from_orm(resource)

@router.put("/{resource_id}", summary="更新教学资源")
async def update_resource(
    resource_id: int,
    resource_in: TeachingResourceUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    resource = await TeachingResourceModel.get_or_none(id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 检查权限：只有上传者或超级管理员可以修改
    if resource.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权修改该资源")

    update_data = resource_in.dict(exclude_unset=True)
    await resource.update_from_dict(update_data)
    await resource.save()

    return TeachingResource.from_orm(resource)

@router.delete("/{resource_id}", summary="删除教学资源")
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    resource = await TeachingResourceModel.get_or_none(id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 检查权限：只有上传者或超级管理员可以删除
    if resource.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除该资源")

    # 删除文件（如果存在）
    if resource.file_path and os.path.exists(resource.file_path):
        os.remove(resource.file_path)

    await resource.delete()
    return {"message": "资源删除成功"}

@router.post("/batch", summary="批量操作资源")
async def batch_operation(
    batch_request: BatchOperationRequest,
    current_user: User = Depends(AuthControl.is_authed)
):
    success_count = 0
    failed_count = 0
    failed_ids = []
    errors = []

    for resource_id in batch_request.target_ids:
        try:
            resource = await TeachingResourceModel.get_or_none(id=resource_id)
            if not resource:
                failed_count += 1
                failed_ids.append(resource_id)
                errors.append(f"资源 {resource_id} 不存在")
                continue

            # 检查权限
            if resource.uploader_id != current_user.id and not current_user.is_superuser:
                failed_count += 1
                failed_ids.append(resource_id)
                errors.append(f"无权操作资源 {resource_id}")
                continue

            # 执行批量操作
            if batch_request.operation == "delete":
                # 删除文件
                if resource.file_path and os.path.exists(resource.file_path):
                    os.remove(resource.file_path)
                await resource.delete()
            elif batch_request.operation == "public":
                await resource.update_from_dict({"is_public": True})
                await resource.save()
            elif batch_request.operation == "private":
                await resource.update_from_dict({"is_public": False})
                await resource.save()
            else:
                failed_count += 1
                failed_ids.append(resource_id)
                errors.append(f"不支持的操作类型: {batch_request.operation}")
                continue

            success_count += 1

        except Exception as e:
            failed_count += 1
            failed_ids.append(resource_id)
            errors.append(f"操作资源 {resource_id} 时出错: {str(e)}")

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        errors=errors
    )

@router.get("/hot/list", summary="获取热门资源")
async def get_hot_resources(
    limit: int = Query(10, ge=1, le=50, description="获取数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    resources = await resource_service.get_hot_resources(limit)
    return [TeachingResource.from_orm(resource) for resource in resources]

@router.get("/download/{file_uuid}", summary="下载文件")
async def download_file(
    file_uuid: str,
    current_user: User = Depends(AuthControl.is_authed)
):
    # 根据文件UUID查找资源
    resource = await TeachingResourceModel.get_or_none(file_url__contains=file_uuid)
    if not resource:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 检查权限
    if not resource.is_public and resource.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权下载该文件")

    if not resource.file_path or not os.path.exists(resource.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 流式返回文件
    def iterfile():
        with open(resource.file_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={resource.title}"}
    )

@router.get("/types/list", summary="获取资源类型列表")
async def get_resource_types(
    current_user: User = Depends(AuthControl.is_authed)
):
    types = [
        {"value": "document", "label": "文档"},
        {"value": "video", "label": "视频"},
        {"value": "audio", "label": "音频"},
        {"value": "image", "label": "图片"},
        {"value": "presentation", "label": "演示文稿"},
        {"value": "simulation", "label": "虚拟仿真"},
        {"value": "link", "label": "外部链接"},
        {"value": "other", "label": "其他"}
    ]
    return types

@router.get("/themes/list", summary="获取思政主题列表")
async def get_ideological_themes(
    current_user: User = Depends(AuthControl.is_authed)
):
    # 返回常见思政主题
    themes = [
        "工匠精神",
        "创新精神",
        "团队协作",
        "责任担当",
        "诚信品质",
        "法治意识",
        "科学精神",
        "人文素养",
        "家国情怀",
        "国际视野"
    ]
    return themes
