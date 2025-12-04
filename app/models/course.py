"""
课程模型
"""
from tortoise import fields
from tortoise.models import Model


class Course(Model):
    """课程表"""
    id = fields.BigIntField(pk=True, description="课程ID")
    code = fields.CharField(max_length=50, unique=True, description="课程代码")
    name = fields.CharField(max_length=200, description="课程名称")
    description = fields.TextField(null=True, description="课程描述")
    credit = fields.DecimalField(max_digits=3, decimal_places=1, null=True, description="学分")
    hours = fields.IntField(null=True, description="学时")
    semester = fields.CharField(max_length=20, null=True, description="开课学期")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_by_id = fields.BigIntField(null=True, description="创建人ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "courses"
        table_description = "课程表"
