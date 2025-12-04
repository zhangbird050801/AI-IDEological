"""
案例分类管理控制器
"""
from typing import List, Optional
from fastapi import HTTPException
from tortoise.functions import Count
from app.models.case_category import CaseCategory, CaseCategoryRelation
from app.schemas.case_category import CaseCategoryCreate, CaseCategoryUpdate, CaseCategoryOut, CaseCategoryTree


class CaseCategoryController:
    """案例分类管理控制器"""

    @staticmethod
    async def get_all_categories() -> List[CaseCategoryOut]:
        """获取所有分类（扁平列表）"""
        categories = await CaseCategory.filter(is_active=True).order_by('order', 'id')
        return [CaseCategoryOut.from_orm(cat) for cat in categories]

    @staticmethod
    async def get_category_tree() -> List[CaseCategoryTree]:
        """获取分类树结构"""
        # 获取所有分类
        categories = await CaseCategory.filter(is_active=True).order_by('order', 'id')

        # 统计每个分类下直接关联的案例数量
        category_ids = [cat.id for cat in categories]
        case_count_map = {}
        if category_ids:
            case_counts = await (
                CaseCategoryRelation
                .filter(category_id__in=category_ids)
                .annotate(case_count=Count("id"))
                .group_by("category_id")
                .values("category_id", "case_count")
            )
            case_count_map = {item["category_id"]: item["case_count"] for item in case_counts}
        
        # 转换为字典以便快速查找，并添加case_count和level
        category_dict = {}
        for cat in categories:
            tree_cat = CaseCategoryTree.from_orm(cat)
            tree_cat.case_count = case_count_map.get(cat.id, 0)
            tree_cat.level = 0  # 将在后面计算
            category_dict[cat.id] = tree_cat
        
        # 构建树形结构并计算层级
        tree = []
        for cat in category_dict.values():
            if cat.parent_id == 0 or cat.parent_id is None:
                # 顶级分类
                cat.level = 0
                tree.append(cat)
            else:
                # 子分类，添加到父分类的children中
                parent = category_dict.get(cat.parent_id)
                if parent:
                    cat.level = parent.level + 1
                    parent.children.append(cat)
        
        # 递归计算父分类的案例总数（包含所有子分类的案例）
        def calculate_total_cases(category: CaseCategoryTree) -> int:
            total = category.case_count
            for child in category.children:
                total += calculate_total_cases(child)
            category.case_count = total
            return total
        
        # 为所有顶级分类计算总案例数
        for cat in tree:
            calculate_total_cases(cat)
        
        return tree

    @staticmethod
    async def get_category(category_id: int) -> CaseCategoryOut:
        """获取分类详情"""
        category = await CaseCategory.filter(id=category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        return CaseCategoryOut.from_orm(category)

    @staticmethod
    async def create_category(category_data: CaseCategoryCreate) -> CaseCategoryOut:
        """创建分类"""
        # 如果有父分类，验证父分类是否存在
        if category_data.parent_id and category_data.parent_id != 0:
            parent = await CaseCategory.filter(id=category_data.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="父分类不存在")
        
        category = await CaseCategory.create(**category_data.dict())
        return CaseCategoryOut.from_orm(category)

    @staticmethod
    async def update_category(category_id: int, category_data: CaseCategoryUpdate) -> CaseCategoryOut:
        """更新分类"""
        category = await CaseCategory.filter(id=category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        # 如果更新父分类，验证不会形成循环引用
        if category_data.parent_id is not None and category_data.parent_id != 0:
            if category_data.parent_id == category_id:
                raise HTTPException(status_code=400, detail="不能将分类设置为自己的子分类")
            
            # 检查是否会形成循环
            if await CaseCategoryController._would_create_cycle(category_id, category_data.parent_id):
                raise HTTPException(status_code=400, detail="不能将分类移动到其子分类下")
        
        update_data = category_data.dict(exclude_unset=True)
        await category.update_from_dict(update_data).save()
        return CaseCategoryOut.from_orm(category)

    @staticmethod
    async def delete_category(category_id: int) -> None:
        """删除分类"""
        category = await CaseCategory.filter(id=category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        # 检查是否有子分类
        children = await CaseCategory.filter(parent_id=category_id).count()
        if children > 0:
            raise HTTPException(status_code=400, detail="该分类包含子分类，请先删除子分类")
        
        # TODO: 检查是否有关联的案例
        # case_count = await Case.filter(category_ids__contains=category_id).count()
        # if case_count > 0:
        #     raise HTTPException(status_code=400, detail=f"该分类包含 {case_count} 个案例，请先移除关联")
        
        await category.delete()

    @staticmethod
    async def move_category(category_id: int, new_parent_id: Optional[int], order_num: int = 0) -> CaseCategoryOut:
        """移动分类到新的父分类下"""
        category = await CaseCategory.filter(id=category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        # 验证新父分类
        if new_parent_id and new_parent_id != 0:
            if new_parent_id == category_id:
                raise HTTPException(status_code=400, detail="不能将分类移动到自己下面")
            
            parent = await CaseCategory.filter(id=new_parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="目标父分类不存在")
            
            # 检查是否会形成循环
            if await CaseCategoryController._would_create_cycle(category_id, new_parent_id):
                raise HTTPException(status_code=400, detail="不能将分类移动到其子分类下")
        
        # 更新分类
        category.parent_id = new_parent_id or 0
        category.order = order_num
        await category.save()
        
        return CaseCategoryOut.from_orm(category)

    @staticmethod
    async def _would_create_cycle(category_id: int, new_parent_id: int) -> bool:
        """检查移动分类是否会形成循环引用"""
        current_id = new_parent_id
        visited = set()
        
        while current_id and current_id != 0:
            if current_id == category_id:
                return True
            
            if current_id in visited:
                # 已经存在循环，但不是由当前操作引起的
                break
            
            visited.add(current_id)
            
            parent = await CaseCategory.filter(id=current_id).first()
            if not parent:
                break
            
            current_id = parent.parent_id
        
        return False
