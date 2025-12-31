from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from tortoise.queryset import Q
from app.schemas.ideological import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplate,
    TemplateSearchRequest,
    BatchOperationRequest,
    BatchOperationResponse,
    AIGCGenerationRequest,
    AIGCGenerationResponse,
)
from app.models.ideological import PromptTemplate as PromptTemplateModel
from app.models.admin import User
from app.core.dependency import AuthControl
from app.core.crud import CRUDBase
import re
import time

router = APIRouter()

class TemplateService(CRUDBase[PromptTemplateModel, PromptTemplateCreate, PromptTemplateUpdate]):
    def __init__(self):
        super().__init__(PromptTemplateModel)

    async def create_template(self, obj_in: PromptTemplateCreate, user_id: int) -> PromptTemplateModel:
        obj_data = obj_in.dict()
        obj_data["creator_id"] = user_id

        # 提取模板中的变量
        template_content = obj_data["template_content"]
        variables = re.findall(r'\{\{(\w+)\}\}', template_content)
        obj_data["variables"] = list(set(variables))  # 去重

        return await self.create(obj_data)

    async def get_templates_with_search(self, search_request: TemplateSearchRequest, user_id: int = None):
        query = PromptTemplateModel.all().filter(is_active=True)

        # 关键词搜索
        if search_request.keyword:
            keyword = search_request.keyword.strip()
            query = query.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(template_content__icontains=keyword)
            )

        # 其他筛选条件
        if search_request.template_type:
            query = query.filter(template_type=search_request.template_type)

        if search_request.category:
            query = query.filter(category__icontains=search_request.category)

        if search_request.software_engineering_chapter:
            query = query.filter(software_engineering_chapter__icontains=search_request.software_engineering_chapter)

        if search_request.theme_category_id:
            query = query.filter(theme_category_id=search_request.theme_category_id)

        # 排序：按评分倒序，按使用次数倒序，系统模板优先
        query = query.order_by("-is_system", "-rating", "-usage_count")

        # 分页
        offset = (search_request.page - 1) * search_request.page_size
        total = await query.count()
        items = await query.offset(offset).limit(search_request.page_size).prefetch_related('creator')

        return {
            "items": items,
            "total": total,
            "page": search_request.page,
            "page_size": search_request.page_size,
            "pages": (total + search_request.page_size - 1) // search_request.page_size
        }

    async def update_template_rating(self, template_id: int, new_rating: int):
        template = await PromptTemplateModel.get_or_none(id=template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")

        # 更新评分
        current_rating_total = template.rating * template.rating_count
        new_rating_count = template.rating_count + 1
        new_average_rating = (current_rating_total + new_rating) / new_rating_count

        await template.update_from_dict({
            "rating": round(new_average_rating, 2),
            "rating_count": new_rating_count
        })
        await template.save()

        return template

    async def get_system_templates(self):
        return await PromptTemplateModel.filter(is_system=True, is_active=True).order_by("category", "name")

    async def render_template(self, template_id: int, variables: dict):
        template = await PromptTemplateModel.get_or_none(id=template_id, is_active=True)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在或已禁用")

        # 渲染模板
        content = template.template_content
        for var, value in variables.items():
            placeholder = f"{{{{{var}}}}}"
            content = content.replace(placeholder, str(value))

        # 增加使用次数
        await template.update_from_dict({"usage_count": template.usage_count + 1})
        await template.save()

        return content

template_service = TemplateService()

@router.get("/", summary="获取提示词模板列表")
async def get_templates(
    keyword: str = Query(None, description="关键词搜索"),
    template_type: str = Query(None, description="模板类型"),
    category: str = Query(None, description="分类"),
    software_engineering_chapter: str = Query(None, description="适用章节"),
    theme_category_id: int = Query(None, description="思政主题分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    search_request = TemplateSearchRequest(
        keyword=keyword,
        template_type=template_type,
        category=category,
        software_engineering_chapter=software_engineering_chapter,
        theme_category_id=theme_category_id,
        page=page,
        page_size=page_size
    )

    result = await template_service.get_templates_with_search(search_request, current_user.id)

    # 转换为响应格式
    templates = [PromptTemplate.model_validate(item) for item in result["items"]]

    return {
        "items": templates,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "pages": result["pages"]
    }

@router.post("/", summary="创建提示词模板")
async def create_template(
    template_in: PromptTemplateCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    template = await template_service.create_template(template_in, current_user.id)
    return PromptTemplate.model_validate(template)

@router.get("/{template_id}", summary="获取提示词模板详情")
async def get_template(
    template_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    template = await PromptTemplateModel.get_or_none(id=template_id).prefetch_related('creator')
    if not template or not template.is_active:
        raise HTTPException(status_code=404, detail="模板不存在或已禁用")

    return PromptTemplate.model_validate(template)

@router.put("/{template_id}", summary="更新提示词模板")
async def update_template(
    template_id: int,
    template_in: PromptTemplateUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    template = await PromptTemplateModel.get_or_none(id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查权限：只有创建者或超级管理员可以修改系统模板
    if template.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权修改该模板")

    # 系统模板只有超级管理员可以修改
    if template.is_system and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权修改系统模板")

    update_data = template_in.dict(exclude_unset=True)

    # 如果更新了模板内容，重新提取变量
    if "template_content" in update_data:
        variables = re.findall(r'\{\{(\w+)\}\}', update_data["template_content"])
        update_data["variables"] = list(set(variables))

    await template.update_from_dict(update_data)
    await template.save()

    return PromptTemplate.model_validate(template)

@router.delete("/{template_id}", summary="删除提示词模板")
async def delete_template(
    template_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    template = await PromptTemplateModel.get_or_none(id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查权限：只有创建者或超级管理员可以删除
    if template.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除该模板")

    # 系统模板只有超级管理员可以删除
    if template.is_system and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除系统模板")

    await template.delete()
    return {"message": "模板删除成功"}

@router.post("/batch", summary="批量操作模板")
async def batch_operation(
    batch_request: BatchOperationRequest,
    current_user: User = Depends(AuthControl.is_authed)
):
    success_count = 0
    failed_count = 0
    failed_ids = []
    errors = []

    for template_id in batch_request.target_ids:
        try:
            template = await PromptTemplateModel.get_or_none(id=template_id)
            if not template:
                failed_count += 1
                failed_ids.append(template_id)
                errors.append(f"模板 {template_id} 不存在")
                continue

            # 检查权限
            if template.creator_id != current_user.id and not current_user.is_superuser:
                failed_count += 1
                failed_ids.append(template_id)
                errors.append(f"无权操作模板 {template_id}")
                continue

            # 系统模板只有超级管理员可以操作
            if template.is_system and not current_user.is_superuser:
                failed_count += 1
                failed_ids.append(template_id)
                errors.append(f"无权操作系统模板 {template_id}")
                continue

            # 执行批量操作
            if batch_request.operation == "delete":
                await template.delete()
            elif batch_request.operation == "activate":
                await template.update_from_dict({"is_active": True})
                await template.save()
            elif batch_request.operation == "deactivate":
                await template.update_from_dict({"is_active": False})
                await template.save()
            else:
                failed_count += 1
                failed_ids.append(template_id)
                errors.append(f"不支持的操作类型: {batch_request.operation}")
                continue

            success_count += 1

        except Exception as e:
            failed_count += 1
            failed_ids.append(template_id)
            errors.append(f"操作模板 {template_id} 时出错: {str(e)}")

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        errors=errors
    )

@router.get("/system/list", summary="获取系统模板列表")
async def get_system_templates(
    current_user: User = Depends(AuthControl.is_authed)
):
    templates = await template_service.get_system_templates()
    return [PromptTemplate.model_validate(template) for template in templates]

@router.get("/statistics/mine", summary="获取我的模板统计")
async def get_my_templates_statistics(
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取当前用户的模板统计信息"""
    total = await PromptTemplateModel.filter(creator_id=current_user.id).count()
    active = await PromptTemplateModel.filter(creator_id=current_user.id, is_active=True).count()
    inactive = await PromptTemplateModel.filter(creator_id=current_user.id, is_active=False).count()
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive
    }

@router.post("/{template_id}/rate", summary="评分模板")
async def rate_template(
    template_id: int,
    rating: int = Query(..., ge=1, le=5, description="评分(1-5)"),
    current_user: User = Depends(AuthControl.is_authed)
):
    template = await template_service.update_template_rating(template_id, rating)
    return PromptTemplate.model_validate(template)

@router.post("/{template_id}/use", summary="使用模板（增加使用次数）")
async def use_template(
    template_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    template = await PromptTemplateModel.get_or_none(id=template_id, is_active=True)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在或已禁用")

    await template.update_from_dict({"usage_count": template.usage_count + 1})
    await template.save()
    return PromptTemplate.model_validate(template)

@router.post("/{template_id}/render", summary="渲染模板")
async def render_template(
    template_id: int,
    variables: dict,
    current_user: User = Depends(AuthControl.is_authed)
):
    rendered_content = await template_service.render_template(template_id, variables)
    return {"rendered_content": rendered_content}

@router.get("/types/list", summary="获取模板类型列表")
async def get_template_types(
    current_user: User = Depends(AuthControl.is_authed)
):
    types = [
        {"value": "case_generation", "label": "案例生成"},
        {"value": "discussion_generation", "label": "讨论题生成"},
        {"value": "thinking_generation", "label": "思考题生成"},
        {"value": "content_optimization", "label": "内容优化"},
        {"value": "teaching_design", "label": "教学设计"},
        {"value": "knowledge_point", "label": "知识点讲解"}
    ]
    return types

@router.get("/categories/list", summary="获取模板分类列表")
async def get_template_categories(
    current_user: User = Depends(AuthControl.is_authed)
):
    categories = [
        "思政案例",
        "教学方法",
        "知识点讲解",
        "课程设计",
        "实践指导",
        "质量评价",
        "前沿技术",
        "职业素养"
    ]
    return categories

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
