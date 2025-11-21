from enum import Enum, StrEnum


class EnumBase(Enum):
    @classmethod
    def get_member_values(cls):
        return [item.value for item in cls._member_map_.values()]

    @classmethod
    def get_member_names(cls):
        return [name for name in cls._member_names_]


class MethodType(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class CaseStatus(StrEnum):
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    PUBLISHED = "published"  # 已发布


class CaseType(StrEnum):
    CASE_STUDY = "case_study"  # 案例分析
    DISCUSSION = "discussion"  # 讨论题
    THINKING = "thinking"  # 思考题
    EXAMPLE = "example"  # 示例
    PRACTICE = "practice"  # 实践项目


class ResourceType(StrEnum):
    DOCUMENT = "document"  # 文档
    VIDEO = "video"  # 视频
    AUDIO = "audio"  # 音频
    IMAGE = "image"  # 图片
    PRESENTATION = "presentation"  # 演示文稿
    SIMULATION = "simulation"  # 虚拟仿真
    LINK = "link"  # 外部链接
    OTHER = "other"  # 其他


class TemplateType(StrEnum):
    CASE_GENERATION = "case_generation"  # 案例生成
    DISCUSSION_GENERATION = "discussion_generation"  # 讨论题生成
    THINKING_GENERATION = "thinking_generation"  # 思考题生成
    CONTENT_OPTIMIZATION = "content_optimization"  # 内容优化
    TEACHING_DESIGN = "teaching_design"  # 教学设计
    KNOWLEDGE_POINT = "knowledge_point"  # 知识点讲解


class PromptAssistantSession(StrEnum):
    GREETING = "greeting"  # 问候阶段
    REQUIREMENT_GATHERING = "requirement_gathering"  # 需求收集阶段
    CLARIFICATION = "clarification"  # 澄清阶段
    DRAFTING = "drafting"  # 草稿阶段
    REFINEMENT = "refinement"  # 优化阶段
    FINALIZATION = "finalization"  # 最终确认阶段
    COMPLETED = "completed"  # 已完成
