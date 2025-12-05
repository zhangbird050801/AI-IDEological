from tortoise import fields
from tortoise.models import Model


class IdeologicalThemeCategory(Model):
    """思政主题分类模型"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="分类名称", index=True)
    description = fields.TextField(null=True, description="分类描述")
    parent_id = fields.IntField(null=True, description="父分类ID", index=True)
    order = fields.IntField(default=0, description="排序", index=True)
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "ideological_theme_categories"
        table_description = "思政主题分类表"
