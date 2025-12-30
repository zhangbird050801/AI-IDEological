from collections import Counter
from typing import List, Optional

from app.models.ideological import IdeologicalCase, TeachingResource, UserFavorites, UserRating, GenerationHistory
from app.models.theme_category import IdeologicalThemeCategory


class RecommendationService:
    @staticmethod
    async def get_case_recommendations(
        user_id: int,
        limit: int = 10,
        theme_category_id: Optional[int] = None,
        difficulty_level: Optional[int] = None,
    ) -> List[IdeologicalCase]:
        query = IdeologicalCase.filter(is_public=True, status="published")
        if theme_category_id:
            query = query.filter(theme_category_id=theme_category_id)
        if difficulty_level:
            query = query.filter(difficulty_level=difficulty_level)

        candidates = await query.order_by("-rating", "-usage_count").limit(200)
        if not candidates:
            return []

        theme_scores, difficulty_scores, favorite_ids = await RecommendationService._build_user_profile(user_id)
        preferred_themes = {t for t, _ in theme_scores.most_common(3)}
        preferred_difficulty = difficulty_scores.most_common(1)[0][0] if difficulty_scores else None

        scored = []
        for case in candidates:
            score = case.rating * 2 + case.usage_count * 0.1
            if case.theme_category_id in preferred_themes:
                score += 5
            if preferred_difficulty and case.difficulty_level == preferred_difficulty:
                score += 2
            if case.id in favorite_ids:
                score += 1
            scored.append((score, case))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [case for _, case in scored[:limit]]

    @staticmethod
    async def _build_user_profile(user_id: int):
        theme_scores = Counter()
        difficulty_scores = Counter()
        favorite_ids = set()

        favorites = await UserFavorites.filter(target_type="case", user_id=user_id).values_list(
            "target_id", flat=True
        )
        favorite_ids = set(favorites or [])

        rated = await UserRating.filter(target_type="case", user_id=user_id).values_list(
            "target_id", flat=True
        )

        case_ids = set(favorite_ids) | set(rated or [])
        if case_ids:
            cases = await IdeologicalCase.filter(id__in=case_ids)
            for case in cases:
                if case.theme_category_id:
                    theme_scores[case.theme_category_id] += 3 if case.id in favorite_ids else 2
                difficulty_scores[case.difficulty_level] += 2

        history_themes = await GenerationHistory.filter(user_id=user_id).exclude(
            ideological_theme=None
        ).values_list("ideological_theme", flat=True)
        if history_themes:
            theme_ids = await IdeologicalThemeCategory.filter(
                name__in=set(history_themes)
            ).values_list("name", "id")
            theme_map = {name: theme_id for name, theme_id in theme_ids}
            for theme_name in history_themes:
                theme_id = theme_map.get(theme_name)
                if theme_id:
                    theme_scores[theme_id] += 1

        return theme_scores, difficulty_scores, favorite_ids

    @staticmethod
    async def get_resource_recommendations(
        course_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        theme_category_id: Optional[int] = None,
        resource_types: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[TeachingResource]:
        query = TeachingResource.filter(is_public=True)
        if course_id:
            query = query.filter(course_id=course_id)
        if chapter_id:
            query = query.filter(chapter_id=chapter_id)
        if theme_category_id:
            query = query.filter(theme_category_id=theme_category_id)
        if resource_types:
            query = query.filter(resource_type__in=resource_types)

        return await query.order_by("-usage_count", "-created_at").limit(limit)
