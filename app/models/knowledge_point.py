"""
知识点模型
"""
from tortoise import fields
from tortoise.models import Model


class KnowledgePoint(Model):
    """知识点表"""
    id = fields.BigIntField(pk=True, description="知识点ID")
    chapter_id = fields.BigIntField(description="章节ID")
    name = fields.CharField(max_length=200, description="知识点名称")
    description = fields.TextField(null=True, description="知识点描述")
    difficulty = fields.IntField(default=3, description="难度等级1-5")
    importance = fields.IntField(default=3, description="重要程度1-5")
    keywords = fields.JSONField(default=list, description="关键词")
    order = fields.IntField(default=0, description="排序")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "knowledge_points"
        table_description = "知识点表"
