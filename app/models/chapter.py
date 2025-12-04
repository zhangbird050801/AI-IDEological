"""
章节模型
"""
from tortoise import fields
from tortoise.models import Model


class Chapter(Model):
    """章节表"""
    id = fields.BigIntField(pk=True, description="章节ID")
    course_id = fields.BigIntField(description="课程ID")
    parent_id = fields.BigIntField(default=0, description="父章节ID，0表示顶级章节")
    name = fields.CharField(max_length=200, description="章节名称")
    description = fields.TextField(null=True, description="章节描述")
    order = fields.IntField(default=0, description="排序")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "chapters"
        table_description = "章节表"
