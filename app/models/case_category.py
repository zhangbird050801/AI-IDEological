"""
案例分类模型
"""
from tortoise import fields
from tortoise.models import Model


class CaseCategory(Model):
    """案例分类表"""
    id = fields.BigIntField(pk=True, description="分类ID")
    parent_id = fields.BigIntField(default=0, description="父分类ID，0表示顶级分类")
    name = fields.CharField(max_length=100, description="分类名称")
    description = fields.TextField(null=True, description="分类描述")
    icon = fields.CharField(max_length=100, null=True, description="图标")
    color = fields.CharField(max_length=20, null=True, description="颜色")
    order = fields.IntField(default=0, description="排序")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "case_categories"
        table_description = "案例分类表"


class CaseCategoryRelation(Model):
    """案例-分类关联表"""
    id = fields.BigIntField(pk=True, description="关联ID")
    case_id = fields.BigIntField(description="案例ID", index=True)
    category_id = fields.BigIntField(description="分类ID", index=True)

    class Meta:
        table = "case_category_rel"
        table_description = "案例-分类关联表"
