from tortoise import fields
from .base import BaseModel, TimestampMixin
from .enums import CaseStatus, CaseType, ResourceType, TemplateType, PromptAssistantSession


class IdeologicalCase(BaseModel, TimestampMixin):
    """课程思政案例库"""
    title = fields.CharField(max_length=200, description="案例标题", index=True)
    content = fields.TextField(description="案例内容")
    software_engineering_chapter = fields.CharField(max_length=100, description="软件工程章节", index=True)
    ideological_theme = fields.CharField(max_length=100, description="思政主题", index=True)
    case_type = fields.CharEnumField(CaseType, description="案例类型", index=True)
    tags = fields.JSONField(default=list, description="标签列表")
    key_points = fields.JSONField(default=list, description="关键知识点")
    discussion_questions = fields.JSONField(default=list, description="讨论问题")
    teaching_suggestions = fields.TextField(null=True, description="教学建议")
    difficulty_level = fields.IntField(default=1, description="难度等级(1-5)", index=True)
    usage_count = fields.IntField(default=0, description="使用次数", index=True)
    rating = fields.FloatField(default=0.0, description="评分(0-5)", index=True)
    rating_count = fields.IntField(default=0, description="评分人数", index=True)
    is_public = fields.BooleanField(default=True, description="是否公开", index=True)
    status = fields.CharEnumField(CaseStatus, default=CaseStatus.DRAFT, description="状态", index=True)
    reviewer_comment = fields.TextField(null=True, description="审核意见")

    # 关系字段
    author = fields.ForeignKeyField('models.User', related_name='authored_cases', null=True, on_delete=fields.SET_NULL)
    reviewer = fields.ForeignKeyField('models.User', related_name='reviewed_cases', null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "ideological_case"


class PromptTemplate(BaseModel, TimestampMixin):
    """提示词模板库"""
    name = fields.CharField(max_length=100, description="模板名称", index=True)
    description = fields.TextField(description="模板描述")
    template_type = fields.CharEnumField(TemplateType, description="模板类型", index=True)
    template_content = fields.TextField(description="模板内容")
    variables = fields.JSONField(default=list, description="模板变量")
    category = fields.CharField(max_length=50, description="分类", index=True)
    software_engineering_chapter = fields.CharField(max_length=100, null=True, description="适用章节", index=True)
    ideological_theme = fields.CharField(max_length=100, null=True, description="思政主题", index=True)
    usage_count = fields.IntField(default=0, description="使用次数", index=True)
    is_system = fields.BooleanField(default=False, description="是否系统模板", index=True)
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)
    rating = fields.FloatField(default=0.0, description="评分(0-5)", index=True)
    rating_count = fields.IntField(default=0, description="评分人数", index=True)

    # 关系字段
    creator = fields.ForeignKeyField('models.User', related_name='created_templates', null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "prompt_template"


class TeachingResource(BaseModel, TimestampMixin):
    """教学资源库"""
    title = fields.CharField(max_length=200, description="资源标题", index=True)
    description = fields.TextField(null=True, description="资源描述")
    resource_type = fields.CharEnumField(ResourceType, description="资源类型", index=True)
    file_url = fields.CharField(max_length=500, null=True, description="文件URL")
    file_size = fields.IntField(null=True, description="文件大小(字节)")
    file_format = fields.CharField(max_length=20, null=True, description="文件格式")
    download_url = fields.CharField(max_length=500, null=True, description="下载链接")
    preview_url = fields.CharField(max_length=500, null=True, description="预览链接")
    external_url = fields.CharField(max_length=500, null=True, description="外部链接")
    tags = fields.JSONField(default=list, description="标签列表")
    software_engineering_chapter = fields.CharField(max_length=100, null=True, description="适用章节", index=True)
    ideological_theme = fields.CharField(max_length=100, null=True, description="思政主题", index=True)
    usage_count = fields.IntField(default=0, description="使用次数", index=True)
    is_public = fields.BooleanField(default=True, description="是否公开", index=True)
    file_path = fields.CharField(max_length=500, null=True, description="文件路径")

    # 关系字段
    uploader = fields.ForeignKeyField('models.User', related_name='uploaded_resources', null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "teaching_resource"


class GenerationHistory(BaseModel, TimestampMixin):
    """生成历史记录"""
    user_input = fields.TextField(description="用户输入")
    generated_content = fields.TextField(description="生成内容")
    generation_type = fields.CharField(max_length=50, description="生成类型", index=True)
    software_engineering_chapter = fields.CharField(max_length=100, null=True, description="软件工程章节", index=True)
    ideological_theme = fields.CharField(max_length=100, null=True, description="思政主题", index=True)
    token_count = fields.IntField(null=True, description="Token消耗数量")
    generation_time = fields.IntField(null=True, description="生成耗时(毫秒)")
    user_rating = fields.IntField(null=True, description="用户评分(1-5)", index=True)
    user_feedback = fields.TextField(null=True, description="用户反馈")
    is_saved_to_case = fields.BooleanField(default=False, description="是否已保存为案例", index=True)

    # 关系字段
    user = fields.ForeignKeyField('models.User', related_name='generation_histories', null=True, on_delete=fields.SET_NULL)
    prompt_template = fields.ForeignKeyField('models.PromptTemplate', related_name='generation_histories', null=True, on_delete=fields.SET_NULL)
    case = fields.ForeignKeyField('models.IdeologicalCase', related_name='generation_histories', null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "generation_history"


class UserFavorites(BaseModel, TimestampMixin):
    """用户收藏"""
    target_type = fields.CharField(max_length=50, description="收藏类型(case/template/resource)", index=True)
    target_id = fields.IntField(description="目标ID", index=True)

    # 关系字段
    user = fields.ForeignKeyField('models.User', related_name='favorites', null=True, on_delete=fields.CASCADE)

    class Meta:
        table = "user_favorites"


class UserRating(BaseModel, TimestampMixin):
    """用户评分"""
    target_type = fields.CharField(max_length=50, description="评分类型(case/template)", index=True)
    target_id = fields.IntField(description="目标ID", index=True)
    rating = fields.IntField(description="评分(1-5)", index=True)
    comment = fields.TextField(null=True, description="评论")

    # 关系字段
    user = fields.ForeignKeyField('models.User', related_name='ratings', null=True, on_delete=fields.CASCADE)

    class Meta:
        table = "user_rating"


class PromptAssistantConversation(BaseModel, TimestampMixin):
    """提示词助手对话记录"""
    session_id = fields.CharField(max_length=100, description="会话ID", index=True)
    user_message = fields.TextField(description="用户消息")
    assistant_message = fields.TextField(description="助手回复")
    session_stage = fields.CharEnumField(PromptAssistantSession, default=PromptAssistantSession.GREETING, description="会话阶段")
    extracted_requirements = fields.JSONField(default=dict, description="提取的需求信息")
    suggested_prompt = fields.TextField(null=True, description="建议的提示词")
    user_feedback = fields.TextField(null=True, description="用户反馈")
    is_final_prompt_generated = fields.BooleanField(default=False, description="是否已生成最终提示词")
    final_prompt = fields.TextField(null=True, description="最终生成的提示词")
    token_count = fields.IntField(null=True, description="Token消耗数量")
    generation_time = fields.IntField(null=True, description="生成耗时(毫秒)")

    # 关系字段
    user = fields.ForeignKeyField('models.User', related_name='prompt_assistant_conversations', null=True, on_delete=fields.CASCADE)

    class Meta:
        table = "prompt_assistant_conversation"


class PromptAssistantTemplate(BaseModel, TimestampMixin):
    """提示词助手预置模板"""
    name = fields.CharField(max_length=100, description="模板名称", index=True)
    description = fields.TextField(description="模板描述")
    template_type = fields.CharField(max_length=50, description="模板类型", index=True)
    target_audience = fields.CharField(max_length=100, description="目标受众")
    use_case_scenario = fields.TextField(description="使用场景")
    sample_prompts = fields.JSONField(default=list, description="示例提示词列表")
    key_questions = fields.JSONField(default=list, description="关键问题列表")
    best_practices = fields.JSONField(default=list, description="最佳实践列表")
    common_variables = fields.JSONField(default=list, description="常用变量列表")
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)
    usage_count = fields.IntField(default=0, description="使用次数", index=True)
    rating = fields.FloatField(default=0.0, description="评分(0-5)", index=True)
    rating_count = fields.IntField(default=0, description="评分人数", index=True)

    class Meta:
        table = "prompt_assistant_template"