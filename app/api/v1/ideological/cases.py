from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from tortoise.queryset import Q
from tortoise.expressions import F
from app.schemas.ideological import (
    IdeologicalCaseCreate,
    IdeologicalCaseUpdate,
    IdeologicalCase,
    CaseSearchRequest,
    BatchOperationRequest,
    BatchOperationResponse,
)
from app.models.ideological import IdeologicalCase as IdeologicalCaseModel
from app.models.admin import User
from app.core.dependency import AuthControl
from app.core.crud import CRUDBase

router = APIRouter()

class CaseService(CRUDBase[IdeologicalCaseModel, IdeologicalCaseCreate, IdeologicalCaseUpdate]):
    def __init__(self):
        super().__init__(IdeologicalCaseModel)

    async def create_case(self, obj_in: IdeologicalCaseCreate, user_id: int) -> IdeologicalCaseModel:
        obj_data = obj_in.dict()
        obj_data["author_id"] = user_id
        return await self.create(obj_data)

    async def get_cases_with_search(self, search_request: CaseSearchRequest, user_id: int = None):
        query = IdeologicalCaseModel.all()

        # 如果不是获取所有公开案例，需要根据用户权限过滤
        if user_id:
            query = query.filter(
                Q(is_public=True) | Q(author_id=user_id)
            )
        else:
            query = query.filter(is_public=True)

        # 关键词搜索
        if search_request.keyword:
            keyword = search_request.keyword.strip()
            query = query.filter(
                Q(title__icontains=keyword) |
                Q(content__icontains=keyword) |
                Q(ideological_theme__icontains=keyword)
            )

        # 其他筛选条件
        if search_request.software_engineering_chapter:
            query = query.filter(software_engineering_chapter=search_request.software_engineering_chapter)

        if search_request.ideological_theme:
            query = query.filter(ideological_theme__icontains=search_request.ideological_theme)

        if search_request.case_type:
            query = query.filter(case_type=search_request.case_type)

        if search_request.tags:
            for tag in search_request.tags:
                query = query.filter(tags__contains=tag)

        if search_request.difficulty_level:
            query = query.filter(difficulty_level=search_request.difficulty_level)

        # 排序：按创建时间倒序，按评分倒序
        query = query.order_by("-created_at", "-rating")

        # 分页
        offset = (search_request.page - 1) * search_request.page_size
        total = await query.count()
        items = await query.offset(offset).limit(search_request.page_size).prefetch_related('author')

        return {
            "items": items,
            "total": total,
            "page": search_request.page,
            "page_size": search_request.page_size,
            "pages": (total + search_request.page_size - 1) // search_request.page_size
        }

    async def update_case_rating(self, case_id: int, new_rating: int):
        case = await IdeologicalCaseModel.get_or_none(id=case_id)
        if not case:
            raise HTTPException(status_code=404, detail="案例不存在")

        # 更新评分
        current_rating_total = case.rating * case.rating_count
        new_rating_count = case.rating_count + 1
        new_average_rating = (current_rating_total + new_rating) / new_rating_count

        await case.update_from_dict({
            "rating": round(new_average_rating, 2),
            "rating_count": new_rating_count,
            "usage_count": case.usage_count + 1
        })
        await case.save()

        return case

    async def get_hot_cases(self, limit: int = 10):
        return await IdeologicalCaseModel.filter(
            is_public=True,
            status="published"
        ).order_by("-usage_count", "-rating").limit(limit)

    async def get_recommended_cases(self, user_id: int, limit: int = 10):
        # 简单推荐算法：根据用户历史案例类型和主题推荐
        # 这里可以根据实际需求优化推荐算法
        return await IdeologicalCaseModel.filter(
            is_public=True,
            status="published"
        ).order_by("-rating", "-usage_count").limit(limit)

case_service = CaseService()

@router.get("/", summary="获取案例列表")
async def get_cases(
    keyword: str = Query(None, description="关键词搜索"),
    software_engineering_chapter: str = Query(None, description="软件工程章节"),
    ideological_theme: str = Query(None, description="思政主题"),
    case_type: str = Query(None, description="案例类型"),
    difficulty_level: int = Query(None, ge=1, le=5, description="难度等级"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    search_request = CaseSearchRequest(
        keyword=keyword,
        software_engineering_chapter=software_engineering_chapter,
        ideological_theme=ideological_theme,
        case_type=case_type,
        difficulty_level=difficulty_level,
        page=page,
        page_size=page_size
    )

    result = await case_service.get_cases_with_search(search_request, current_user.id)

    # 转换为响应格式
    cases = [IdeologicalCase.from_orm(item) for item in result["items"]]

    return {
        "items": cases,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "pages": result["pages"]
    }

@router.post("/", summary="创建案例")
async def create_case(
    case_in: IdeologicalCaseCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    case = await case_service.create_case(case_in, current_user.id)
    return IdeologicalCase.from_orm(case)

@router.get("/{case_id}", summary="获取案例详情")
async def get_case(
    case_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    case = await IdeologicalCaseModel.get_or_none(id=case_id).prefetch_related('author')
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查权限
    if not case.is_public and case.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该案例")

    # 增加使用次数
    await case.update_from_dict({"usage_count": case.usage_count + 1})
    await case.save()

    return IdeologicalCase.from_orm(case)

@router.put("/{case_id}", summary="更新案例")
async def update_case(
    case_id: int,
    case_in: IdeologicalCaseUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    case = await IdeologicalCaseModel.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查权限：只有作者或超级管理员可以修改
    if case.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权修改该案例")

    update_data = case_in.dict(exclude_unset=True)
    await case.update_from_dict(update_data)
    await case.save()

    return IdeologicalCase.from_orm(case)

@router.delete("/{case_id}", summary="删除案例")
async def delete_case(
    case_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    case = await IdeologicalCaseModel.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查权限：只有作者或超级管理员可以删除
    if case.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除该案例")

    await case.delete()
    return {"message": "案例删除成功"}

@router.post("/batch", summary="批量操作案例")
async def batch_operation(
    batch_request: BatchOperationRequest,
    current_user: User = Depends(AuthControl.is_authed)
):
    success_count = 0
    failed_count = 0
    failed_ids = []
    errors = []

    for case_id in batch_request.target_ids:
        try:
            case = await IdeologicalCaseModel.get_or_none(id=case_id)
            if not case:
                failed_count += 1
                failed_ids.append(case_id)
                errors.append(f"案例 {case_id} 不存在")
                continue

            # 检查权限
            if case.author_id != current_user.id and not current_user.is_superuser:
                failed_count += 1
                failed_ids.append(case_id)
                errors.append(f"无权操作案例 {case_id}")
                continue

            # 执行批量操作
            if batch_request.operation == "delete":
                await case.delete()
            elif batch_request.operation == "publish":
                await case.update_from_dict({"status": "published"})
                await case.save()
            elif batch_request.operation == "draft":
                await case.update_from_dict({"status": "draft"})
                await case.save()
            elif batch_request.operation == "public":
                await case.update_from_dict({"is_public": True})
                await case.save()
            elif batch_request.operation == "private":
                await case.update_from_dict({"is_public": False})
                await case.save()
            else:
                failed_count += 1
                failed_ids.append(case_id)
                errors.append(f"不支持的操作类型: {batch_request.operation}")
                continue

            success_count += 1

        except Exception as e:
            failed_count += 1
            failed_ids.append(case_id)
            errors.append(f"操作案例 {case_id} 时出错: {str(e)}")

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        errors=errors
    )

@router.get("/hot/list", summary="获取热门案例")
async def get_hot_cases(
    limit: int = Query(10, ge=1, le=50, description="获取数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    cases = await case_service.get_hot_cases(limit)
    return [IdeologicalCase.from_orm(case) for case in cases]

@router.get("/recommended/list", summary="获取推荐案例")
async def get_recommended_cases(
    limit: int = Query(10, ge=1, le=50, description="获取数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    cases = await case_service.get_recommended_cases(current_user.id, limit)
    return [IdeologicalCase.from_orm(case) for case in cases]

@router.post("/{case_id}/rate", summary="评分案例")
async def rate_case(
    case_id: int,
    rating: int = Query(..., ge=1, le=5, description="评分(1-5)"),
    comment: str = Query(None, description="评价内容"),
    current_user: User = Depends(AuthControl.is_authed)
):
    case = await case_service.update_case_rating(case_id, rating)
    # TODO: 将评论保存到数据库（需要创建评论表）
    return IdeologicalCase.from_orm(case)

@router.get("/chapters/list", summary="获取软件工程章节列表")
async def get_chapters(
    current_user: User = Depends(AuthControl.is_authed)
):
    # 返回软件工程常见章节
    chapters = [
        "软件工程概述",
        "软件过程模型",
        "需求分析",
        "系统设计",
        "编码实现",
        "软件测试",
        "软件维护",
        "项目管理",
        "软件质量",
        "软件工程前沿"
    ]
    return chapters

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