from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class IdeologicalCaseBase(BaseModel):
    title: str = Field(..., description="案例标题")
    content: str = Field(..., description="案例内容")
    software_engineering_chapter: str = Field(..., description="软件工程章节")
    ideological_theme: str = Field(..., description="思政主题")
    case_type: str = Field(..., description="案例类型")
    category_ids: List[int] = Field(default_factory=list, description="案例分类ID列表")
    tags: List[str] = Field(default=[], description="标签列表")
    key_points: List[str] = Field(default=[], description="关键知识点")
    discussion_questions: List[str] = Field(default=[], description="讨论问题")
    teaching_suggestions: Optional[str] = Field(None, description="教学建议")
    difficulty_level: int = Field(default=1, ge=1, le=5, description="难度等级")
    is_public: bool = Field(default=True, description="是否公开")


class IdeologicalCaseCreate(IdeologicalCaseBase):
    pass


class IdeologicalCaseUpdate(BaseModel):
    title: Optional[str] = Field(None, description="案例标题")
    content: Optional[str] = Field(None, description="案例内容")
    software_engineering_chapter: Optional[str] = Field(None, description="软件工程章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    case_type: Optional[str] = Field(None, description="案例类型")
    category_ids: Optional[List[int]] = Field(None, description="案例分类ID列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    key_points: Optional[List[str]] = Field(None, description="关键知识点")
    discussion_questions: Optional[List[str]] = Field(None, description="讨论问题")
    teaching_suggestions: Optional[str] = Field(None, description="教学建议")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="难度等级")
    is_public: Optional[bool] = Field(None, description="是否公开")
    status: Optional[str] = Field(None, description="状态")


class IdeologicalCaseInDB(IdeologicalCaseBase):
    id: int
    usage_count: int
    rating: float
    rating_count: int
    status: str
    author_id: int
    reviewer_id: Optional[int] = None
    reviewer_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IdeologicalCase(IdeologicalCaseInDB):
    pass


class PromptTemplateBase(BaseModel):
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    template_type: str = Field(..., description="模板类型")
    template_content: str = Field(..., description="模板内容")
    variables: List[str] = Field(default=[], description="模板变量")
    category: str = Field(..., description="分类")
    software_engineering_chapter: Optional[str] = Field(None, description="适用章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    is_active: bool = Field(default=True, description="是否启用")


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    template_type: Optional[str] = Field(None, description="模板类型")
    template_content: Optional[str] = Field(None, description="模板内容")
    variables: Optional[List[str]] = Field(None, description="模板变量")
    category: Optional[str] = Field(None, description="分类")
    software_engineering_chapter: Optional[str] = Field(None, description="适用章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    is_active: Optional[bool] = Field(None, description="是否启用")


class PromptTemplateInDB(PromptTemplateBase):
    id: int
    usage_count: int
    is_system: bool
    creator_id: Optional[int] = None
    rating: float
    rating_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptTemplate(PromptTemplateInDB):
    pass


class TeachingResourceBase(BaseModel):
    title: str = Field(..., description="资源标题")
    description: Optional[str] = Field(None, description="资源描述")
    resource_type: str = Field(..., description="资源类型")
    external_url: Optional[str] = Field(None, description="外部链接")
    file_url: Optional[str] = Field(None, description="文件访问URL")
    download_url: Optional[str] = Field(None, description="下载URL")
    preview_url: Optional[str] = Field(None, description="预览URL")
    file_path: Optional[str] = Field(None, description="服务器文件路径")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    file_format: Optional[str] = Field(None, description="文件格式")
    tags: List[str] = Field(default=[], description="标签列表")
    software_engineering_chapter: Optional[str] = Field(None, description="适用章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    is_public: bool = Field(default=True, description="是否公开")


class TeachingResourceCreate(TeachingResourceBase):
    pass


class TeachingResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, description="资源标题")
    description: Optional[str] = Field(None, description="资源描述")
    resource_type: Optional[str] = Field(None, description="资源类型")
    external_url: Optional[str] = Field(None, description="外部链接")
    file_url: Optional[str] = Field(None, description="文件访问URL")
    download_url: Optional[str] = Field(None, description="下载URL")
    preview_url: Optional[str] = Field(None, description="预览URL")
    file_path: Optional[str] = Field(None, description="服务器文件路径")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    file_format: Optional[str] = Field(None, description="文件格式")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    software_engineering_chapter: Optional[str] = Field(None, description="适用章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    is_public: Optional[bool] = Field(None, description="是否公开")


class TeachingResourceInDB(TeachingResourceBase):
    id: int
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    usage_count: int
    uploader_id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeachingResource(TeachingResourceInDB):
    pass


class GenerationHistoryBase(BaseModel):
    user_input: str = Field(..., description="用户输入")
    generated_content: str = Field(..., description="生成内容")
    generation_type: str = Field(..., description="生成类型")
    software_engineering_chapter: Optional[str] = Field(None, description="软件工程章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")


class GenerationHistoryCreate(GenerationHistoryBase):
    prompt_template_id: Optional[int] = Field(None, description="使用的提示词模板ID")
    token_count: Optional[int] = Field(None, description="Token消耗数量")
    generation_time: Optional[int] = Field(None, description="生成耗时(毫秒)")
    user_id: int = Field(..., description="用户ID")


class GenerationHistoryUpdate(BaseModel):
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="用户评分")
    user_feedback: Optional[str] = Field(None, description="用户反馈")
    is_saved_to_case: bool = Field(default=False, description="是否已保存为案例")
    case_id: Optional[int] = Field(None, description="关联的案例ID")


class GenerationHistoryInDB(GenerationHistoryBase):
    id: int
    prompt_template_id: Optional[int] = None
    token_count: Optional[int] = None
    generation_time: Optional[int] = None
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    is_saved_to_case: bool
    case_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerationHistory(GenerationHistoryInDB):
    pass


class UserFavoritesBase(BaseModel):
    target_type: str = Field(..., description="收藏类型")
    target_id: int = Field(..., description="目标ID")


class UserFavoritesCreate(UserFavoritesBase):
    user_id: int = Field(..., description="用户ID")


class UserFavorites(UserFavoritesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRatingBase(BaseModel):
    target_type: str = Field(..., description="评分类型")
    target_id: int = Field(..., description="目标ID")
    rating: int = Field(..., ge=1, le=5, description="评分")
    comment: Optional[str] = Field(None, description="评论")


class UserRatingCreate(UserRatingBase):
    user_id: int = Field(..., description="用户ID")


class UserRating(UserRatingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 请求和响应模型
class CaseSearchRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="关键词")
    software_engineering_chapter: Optional[str] = Field(None, description="软件工程章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    case_type: Optional[str] = Field(None, description="案例类型")
    category_ids: Optional[List[int]] = Field(None, description="分类ID列表")
    tags: Optional[List[str]] = Field(None, description="标签")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="难度等级")
    is_public: Optional[bool] = Field(None, description="是否公开")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")


class TemplateSearchRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="关键词")
    template_type: Optional[str] = Field(None, description="模板类型")
    category: Optional[str] = Field(None, description="分类")
    software_engineering_chapter: Optional[str] = Field(None, description="适用章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    is_active: Optional[bool] = Field(None, description="是否启用")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")


class ResourceSearchRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="关键词")
    resource_type: Optional[str] = Field(None, description="资源类型")
    software_engineering_chapter: Optional[str] = Field(None, description="适用章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    tags: Optional[List[str]] = Field(None, description="标签")
    is_public: Optional[bool] = Field(None, description="是否公开")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")


class AIGCGenerationRequest(BaseModel):
    prompt: str = Field(..., description="生成提示")
    template_id: Optional[int] = Field(None, description="使用的模板ID")
    template_variables: Optional[dict] = Field(None, description="模板变量")
    generation_type: str = Field(default="case", description="生成类型")
    software_engineering_chapter: Optional[str] = Field(None, description="软件工程章节")
    ideological_theme: Optional[str] = Field(None, description="思政主题")
    use_stream: bool = Field(default=True, description="是否使用流式生成")


class AIGCGenerationResponse(BaseModel):
    content: str = Field(..., description="生成内容")
    generation_id: Optional[int] = Field(None, description="生成记录ID")
    token_count: Optional[int] = Field(None, description="Token消耗")
    generation_time: Optional[int] = Field(None, description="生成耗时")


class BatchOperationRequest(BaseModel):
    target_ids: List[int] = Field(..., description="目标ID列表")
    operation: str = Field(..., description="操作类型")
    parameters: Optional[dict] = Field(None, description="操作参数")


class BatchOperationResponse(BaseModel):
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    failed_ids: List[int] = Field(default=[], description="失败的ID列表")
    errors: List[str] = Field(default=[], description="错误信息列表")


# 提示词助手相关模型
class PromptAssistantConversationBase(BaseModel):
    session_id: str = Field(..., description="会话ID")
    user_message: str = Field(..., description="用户消息")
    assistant_message: str = Field(..., description="助手回复")
    session_stage: str = Field(default="greeting", description="会话阶段")
    extracted_requirements: dict = Field(default=dict, description="提取的需求信息")
    suggested_prompt: Optional[str] = Field(None, description="建议的提示词")
    user_feedback: Optional[str] = Field(None, description="用户反馈")
    is_final_prompt_generated: bool = Field(default=False, description="是否已生成最终提示词")
    final_prompt: Optional[str] = Field(None, description="最终生成的提示词")
    token_count: Optional[int] = Field(None, description="Token消耗数量")
    generation_time: Optional[int] = Field(None, description="生成耗时(毫秒)")


class PromptAssistantConversationCreate(PromptAssistantConversationBase):
    user_id: int = Field(..., description="用户ID")


class PromptAssistantConversationUpdate(BaseModel):
    user_message: Optional[str] = Field(None, description="用户消息")
    assistant_message: Optional[str] = Field(None, description="助手回复")
    session_stage: Optional[str] = Field(None, description="会话阶段")
    extracted_requirements: Optional[dict] = Field(None, description="提取的需求信息")
    suggested_prompt: Optional[str] = Field(None, description="建议的提示词")
    user_feedback: Optional[str] = Field(None, description="用户反馈")
    is_final_prompt_generated: Optional[bool] = Field(None, description="是否已生成最终提示词")
    final_prompt: Optional[str] = Field(None, description="最终生成的提示词")
    token_count: Optional[int] = Field(None, description="Token消耗数量")
    generation_time: Optional[int] = Field(None, description="生成耗时(毫秒)")


class PromptAssistantConversationInDB(PromptAssistantConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptAssistantConversation(PromptAssistantConversationInDB):
    pass


class PromptAssistantTemplateBase(BaseModel):
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    template_type: str = Field(..., description="模板类型")
    target_audience: str = Field(..., description="目标受众")
    use_case_scenario: str = Field(..., description="使用场景")
    sample_prompts: List[str] = Field(default=[], description="示例提示词列表")
    key_questions: List[str] = Field(default=[], description="关键问题列表")
    best_practices: List[str] = Field(default=[], description="最佳实践列表")
    common_variables: List[str] = Field(default=[], description="常用变量列表")
    is_active: bool = Field(default=True, description="是否启用")


class PromptAssistantTemplateCreate(PromptAssistantTemplateBase):
    pass


class PromptAssistantTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    template_type: Optional[str] = Field(None, description="模板类型")
    target_audience: Optional[str] = Field(None, description="目标受众")
    use_case_scenario: Optional[str] = Field(None, description="使用场景")
    sample_prompts: Optional[List[str]] = Field(None, description="示例提示词列表")
    key_questions: Optional[List[str]] = Field(None, description="关键问题列表")
    best_practices: Optional[List[str]] = Field(None, description="最佳实践列表")
    common_variables: Optional[List[str]] = Field(None, description="常用变量列表")
    is_active: Optional[bool] = Field(None, description="是否启用")


class PromptAssistantTemplateInDB(PromptAssistantTemplateBase):
    id: int
    usage_count: int
    rating: float
    rating_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptAssistantTemplate(PromptAssistantTemplateInDB):
    pass


# 提示词助手请求和响应模型
class PromptAssistantRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，为空则创建新会话")
    context: Optional[dict] = Field(None, description="上下文信息")


class PromptAssistantResponse(BaseModel):
    session_id: str = Field(..., description="会话ID")
    assistant_message: str = Field(..., description="助手回复")
    session_stage: str = Field(..., description="会话阶段")
    extracted_requirements: dict = Field(default=dict, description="提取的需求信息")
    suggested_prompt: Optional[str] = Field(None, description="建议的提示词")
    is_final_prompt_ready: bool = Field(default=False, description="是否准备好最终提示词")
    final_prompt: Optional[str] = Field(None, description="最终生成的提示词")
    token_count: Optional[int] = Field(None, description="Token消耗数量")
    generation_time: Optional[int] = Field(None, description="生成耗时(毫秒)")


class PromptAssistantSessionRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")


class PromptAssistantSessionResponse(BaseModel):
    session_id: str = Field(..., description="会话ID")
    conversation_history: List[PromptAssistantConversation] = Field(..., description="对话历史")
    current_stage: str = Field(..., description="当前阶段")
    extracted_requirements: dict = Field(default=dict, description="提取的需求信息")
    suggested_prompts: List[str] = Field(default=[], description="建议的提示词列表")
    is_completed: bool = Field(default=False, description="是否已完成")
    final_prompt: Optional[str] = Field(None, description="最终提示词")
