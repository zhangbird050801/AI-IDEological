from typing import List, Dict, Set
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi import Body
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
from app.models.ideological import IdeologicalCase as IdeologicalCaseModel, UserFavorites
from app.models.chapter import Chapter
from app.models.admin import User
from app.core.dependency import AuthControl
from app.core.crud import CRUDBase
from app.services.theme_service import ThemeService
from app.services.recommendation_service import RecommendationService

router = APIRouter()

async def enrich_case_with_theme_name(case: IdeologicalCaseModel) -> dict:
    """为案例对象添加主题名称"""
    case_dict = IdeologicalCase.from_orm(case).dict()
    if case.theme_category_id:
        theme_name = await ThemeService.get_theme_name_by_id(case.theme_category_id)
        case_dict['theme_name'] = theme_name
    return case_dict


async def get_favorite_stats(case_ids: List[int], user_id: int) -> (Dict[int, int], Set[int]):
    """获取收藏统计和当前用户收藏集合"""
    if not case_ids:
        return {}, set()

    favorites = await UserFavorites.filter(
        target_type="case",
        target_id__in=case_ids
    ).values("target_id", "user_id")

    counts = Counter([f["target_id"] for f in favorites])
    user_favs = {f["target_id"] for f in favorites if f["user_id"] == user_id}
    return counts, user_favs


async def _hydrate_course_chapter(obj_data: dict) -> dict:
    chapter_id = obj_data.get("chapter_id")
    course_id = obj_data.get("course_id")
    chapter_name = obj_data.get("software_engineering_chapter")

    if chapter_id:
        chapter = await Chapter.get_or_none(id=chapter_id)
        if chapter:
            obj_data["software_engineering_chapter"] = chapter.name
            if not course_id:
                obj_data["course_id"] = chapter.course_id
        return obj_data

    if chapter_name:
        query = Chapter.filter(name=chapter_name)
        if course_id:
            query = query.filter(course_id=course_id)
        chapter = await query.first()
        if chapter:
            obj_data["chapter_id"] = chapter.id
            if not course_id:
                obj_data["course_id"] = chapter.course_id

    return obj_data

class CaseService(CRUDBase[IdeologicalCaseModel, IdeologicalCaseCreate, IdeologicalCaseUpdate]):
    def __init__(self):
        super().__init__(IdeologicalCaseModel)

    async def create_case(self, obj_in: IdeologicalCaseCreate, user_id: int) -> IdeologicalCaseModel:
        obj_data = obj_in.dict()
        obj_data["author_id"] = user_id
        
        # 处理主题转换：如果只有名称没有ID，尝试转换
        obj_data = await ThemeService.process_form_data(obj_data)
        obj_data = await _hydrate_course_chapter(obj_data)
        
        case = await self.create(obj_data)
        return case

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
                Q(content__icontains=keyword)
            )

        # 其他筛选条件
        if search_request.chapter_id and search_request.software_engineering_chapter:
            query = query.filter(
                Q(chapter_id=search_request.chapter_id) |
                Q(software_engineering_chapter=search_request.software_engineering_chapter)
            )
        elif search_request.chapter_id:
            query = query.filter(chapter_id=search_request.chapter_id)
        elif search_request.software_engineering_chapter:
            query = query.filter(software_engineering_chapter=search_request.software_engineering_chapter)

        if search_request.course_id:
            query = query.filter(course_id=search_request.course_id)

        if search_request.theme_category_id:
            query = query.filter(theme_category_id=search_request.theme_category_id)

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

    async def update_case_rating(self, case_id: int, new_rating: float, user_id: int, comment: str = None):
        case = await IdeologicalCaseModel.get_or_none(id=case_id)
        if not case:
            raise HTTPException(status_code=404, detail="案例不存在")

        # 检查用户是否已经评分过
        from app.models.ideological import UserRating
        existing_rating = await UserRating.get_or_none(
            user_id=user_id,
            target_type="case",
            target_id=case_id
        )

        if existing_rating:
            # 用户修改评分，需要重新计算平均分
            old_rating = existing_rating.rating
            current_rating_total = case.rating * case.rating_count
            # 减去旧评分，加上新评分
            new_rating_total = current_rating_total - old_rating + new_rating
            new_average_rating = new_rating_total / case.rating_count
            
            # 更新用户评分记录
            existing_rating.rating = new_rating
            existing_rating.comment = comment
            await existing_rating.save()
        else:
            # 新评分
            current_rating_total = case.rating * case.rating_count
            new_rating_count = case.rating_count + 1
            new_average_rating = (current_rating_total + new_rating) / new_rating_count
            
            # 创建用户评分记录
            await UserRating.create(
                user_id=user_id,
                target_type="case",
                target_id=case_id,
                rating=new_rating,
                comment=comment
            )
            
            # 更新评分人数
            await case.update_from_dict({
                "rating_count": new_rating_count
            })

        # 更新案例的平均评分
        await case.update_from_dict({
            "rating": round(new_average_rating, 2)
        })
        await case.save()

        return case

    async def get_hot_cases(self, limit: int = 10):
        return await IdeologicalCaseModel.filter(
            is_public=True,
            status="published"
        ).order_by("-usage_count", "-rating").limit(limit)

    async def get_recommended_cases(self, user_id: int, limit: int = 10):
        return await RecommendationService.get_case_recommendations(user_id=user_id, limit=limit)

case_service = CaseService()

@router.get("/", summary="获取案例列表")
async def get_cases(
    keyword: str = Query(None, description="关键词搜索"),
    software_engineering_chapter: str = Query(None, description="软件工程章节"),
    course_id: int = Query(None, description="课程ID"),
    chapter_id: int = Query(None, description="章节ID"),
    theme_category_id: int = Query(None, description="思政主题分类ID"),
    case_type: str = Query(None, description="案例类型"),
    difficulty_level: int = Query(None, ge=1, le=5, description="难度等级"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(AuthControl.is_authed)
):
    search_request = CaseSearchRequest(
        keyword=keyword,
        software_engineering_chapter=software_engineering_chapter,
        course_id=course_id,
        chapter_id=chapter_id,
        theme_category_id=theme_category_id,
        case_type=case_type,
        difficulty_level=difficulty_level,
        page=page,
        page_size=page_size
    )

    result = await case_service.get_cases_with_search(search_request, current_user.id)

    # 收藏统计
    case_ids = [item.id for item in result["items"]]
    favorite_counts, user_favorites = await get_favorite_stats(case_ids, current_user.id)

    # 转换为响应格式，并添加主题名称与收藏信息
    cases = []
    for item in result["items"]:
        case_dict = await enrich_case_with_theme_name(item)
        case_dict["favorite_count"] = favorite_counts.get(item.id, 0)
        case_dict["is_favorited"] = item.id in user_favorites
        cases.append(case_dict)

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
    return await enrich_case_with_theme_name(case)

@router.get("/{case_id}", summary="获取案例详情")
async def get_case(
    case_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    from app.models.ideological import UserRating
    
    case = await IdeologicalCaseModel.get_or_none(id=case_id).prefetch_related('author')
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查权限
    if not case.is_public and case.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该案例")

    # 增加使用次数
    await case.update_from_dict({"usage_count": case.usage_count + 1})
    await case.save()

    result = await enrich_case_with_theme_name(case)
    # 收藏信息
    result["favorite_count"] = await UserFavorites.filter(target_type="case", target_id=case_id).count()
    result["is_favorited"] = await UserFavorites.filter(
        target_type="case", target_id=case_id, user_id=current_user.id
    ).exists()
    
    # 当前用户的评分信息
    user_rating = await UserRating.get_or_none(
        target_type="case", 
        target_id=case_id, 
        user_id=current_user.id
    )
    result["user_rating"] = user_rating.rating if user_rating else None
    result["user_comment"] = user_rating.comment if user_rating else None

    return result

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
    
    # 处理主题转换
    update_data = await ThemeService.process_form_data(update_data)
    update_data = await _hydrate_course_chapter(update_data)
    
    await case.update_from_dict(update_data)
    await case.save()

    return await enrich_case_with_theme_name(case)

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


@router.post("/{case_id}/favorite", summary="收藏/取消收藏案例")
async def toggle_case_favorite(
    case_id: int,
    favorited: bool = Body(True, embed=True, description="true: 收藏, false: 取消收藏"),
    current_user: User = Depends(AuthControl.is_authed)
):
    case = await IdeologicalCaseModel.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    existing = await UserFavorites.get_or_none(
        target_type="case", target_id=case_id, user_id=current_user.id
    )

    if favorited and not existing:
        await UserFavorites.create(
            target_type="case",
            target_id=case_id,
            user_id=current_user.id
        )
        await IdeologicalCaseModel.filter(id=case_id).update(favorite_count=F("favorite_count") + 1)
    elif not favorited and existing:
        await existing.delete()
        await IdeologicalCaseModel.filter(id=case_id, favorite_count__gt=0).update(
            favorite_count=F("favorite_count") - 1
        )

    new_count = await UserFavorites.filter(target_type="case", target_id=case_id).count()
    is_favorited = await UserFavorites.filter(
        target_type="case", target_id=case_id, user_id=current_user.id
    ).exists()

    await IdeologicalCaseModel.filter(id=case_id).update(favorite_count=new_count)

    return {
        "favorited": is_favorited,
        "favorite_count": new_count
    }

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
    theme_category_id: int = Query(None, description="思政主题分类ID"),
    difficulty_level: int = Query(None, ge=1, le=5, description="难度等级"),
    current_user: User = Depends(AuthControl.is_authed)
):
    cases = await RecommendationService.get_case_recommendations(
        user_id=current_user.id,
        limit=limit,
        theme_category_id=theme_category_id,
        difficulty_level=difficulty_level
    )
    return [IdeologicalCase.from_orm(case) for case in cases]

@router.get("/statistics/mine", summary="获取我的案例统计")
async def get_my_cases_statistics(
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取当前用户的案例统计信息"""
    total = await IdeologicalCaseModel.filter(author_id=current_user.id).count()
    published = await IdeologicalCaseModel.filter(author_id=current_user.id, status="published").count()
    draft = await IdeologicalCaseModel.filter(author_id=current_user.id, status="draft").count()
    
    return {
        "total": total,
        "published": published,
        "draft": draft
    }

@router.post("/{case_id}/rate", summary="评分案例")
async def rate_case(
    case_id: int,
    rating: float = Query(..., description="评分(1-5，步长0.5)"),
    comment: str = Query(None, description="评价内容"),
    current_user: User = Depends(AuthControl.is_authed)
):
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=422, detail="评分必须在 1 到 5 之间")
    doubled = rating * 2
    if abs(doubled - round(doubled)) > 1e-9:
        raise HTTPException(status_code=422, detail="评分步长必须为 0.5")
    case = await case_service.update_case_rating(case_id, rating, current_user.id, comment)
    return IdeologicalCase.from_orm(case)

@router.get("/chapters/list", summary="获取软件工程章节列表")
async def get_chapters(
    course_id: int = Query(None, description="课程ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    query = Chapter.filter(is_active=True)
    if course_id:
        query = query.filter(course_id=course_id)
    chapters = await query.order_by("order").values_list("name", flat=True)
    return list(chapters)

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
