from typing import List, Optional
from app.models.theme_category import IdeologicalThemeCategory
from app.schemas.theme_category import (
    ThemeCategoryCreate,
    ThemeCategoryUpdate,
    ThemeCategory,
    ThemeCategoryTree
)


class ThemeCategoryController:
    """思政主题分类控制器"""

    async def get_tree(self) -> List[ThemeCategoryTree]:
        """获取分类树"""
        categories = await IdeologicalThemeCategory.filter(is_active=True).order_by('order', 'id')
        return self._build_tree(categories)

    async def get_all(self) -> List[ThemeCategory]:
        """获取所有分类（扁平列表）"""
        categories = await IdeologicalThemeCategory.all().order_by('order', 'id')
        return [ThemeCategory.from_orm(cat) for cat in categories]

    async def get_by_id(self, category_id: int) -> Optional[ThemeCategory]:
        """根据ID获取分类"""
        category = await IdeologicalThemeCategory.get_or_none(id=category_id)
        return ThemeCategory.from_orm(category) if category else None

    async def create(self, category_data: ThemeCategoryCreate) -> ThemeCategory:
        """创建分类"""
        # 如果有父分类，检查父分类是否存在
        if category_data.parent_id:
            parent = await IdeologicalThemeCategory.get_or_none(id=category_data.parent_id)
            if not parent:
                raise ValueError("父分类不存在")

        category = await IdeologicalThemeCategory.create(**category_data.dict())
        return ThemeCategory.from_orm(category)

    async def update(self, category_id: int, category_data: ThemeCategoryUpdate) -> ThemeCategory:
        """更新分类"""
        category = await IdeologicalThemeCategory.get_or_none(id=category_id)
        if not category:
            raise ValueError("分类不存在")

        # 检查父分类
        if category_data.parent_id is not None:
            if category_data.parent_id == category_id:
                raise ValueError("不能将自己设为父分类")
            if category_data.parent_id != 0:
                parent = await IdeologicalThemeCategory.get_or_none(id=category_data.parent_id)
                if not parent:
                    raise ValueError("父分类不存在")

        update_data = category_data.dict(exclude_unset=True)
        await category.update_from_dict(update_data)
        await category.save()
        return ThemeCategory.from_orm(category)

    async def delete(self, category_id: int):
        """删除分类"""
        category = await IdeologicalThemeCategory.get_or_none(id=category_id)
        if not category:
            raise ValueError("分类不存在")

        # 检查是否有子分类
        children = await IdeologicalThemeCategory.filter(parent_id=category_id).count()
        if children > 0:
            raise ValueError("该分类下有子分类，无法删除")

        await category.delete()

    async def move(self, category_id: int, parent_id: Optional[int], order: int):
        """移动分类（用于拖拽排序）"""
        category = await IdeologicalThemeCategory.get_or_none(id=category_id)
        if not category:
            raise ValueError("分类不存在")

        if parent_id == category_id:
            raise ValueError("不能将自己设为父分类")

        if parent_id:
            parent = await IdeologicalThemeCategory.get_or_none(id=parent_id)
            if not parent:
                raise ValueError("父分类不存在")

        category.parent_id = parent_id
        category.order = order
        await category.save()
        return ThemeCategory.from_orm(category)

    def _build_tree(self, categories: List[IdeologicalThemeCategory], parent_id: Optional[int] = None) -> List[ThemeCategoryTree]:
        """构建树形结构"""
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                node = ThemeCategoryTree.from_orm(category)
                node.children = self._build_tree(categories, category.id)
                tree.append(node)
        return tree


# 创建全局实例
theme_category_controller = ThemeCategoryController()
