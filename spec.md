# 基于AIGC的《软件工程》课程思政内容生成及管理系统

## 项目文档 v1.0

---

## 一、项目概述

### 1.1 项目背景

本系统旨在利用生成式人工智能(AIGC)技术，帮助《软件工程》课程教师快速生成和管理课程思政教学内容。通过深度整合课程体系、微课素材、虚拟仿真资源等多元教学内容，教师可以通过与AIGC工具的对话互动，迅速获得即时建议并生成相关思政案例，显著提升教学效果和效率。

### 1.2 技术架构

- **后端框架**: FastAPI + Python 3.11
- **前端框架**: Vue3 + Naive UI + Vite
- **数据库**: SQLite (可扩展至MySQL/PostgreSQL)
- **ORM**: Tortoise ORM
- **AI集成**: OpenAI API / 国产大模型
- **权限管理**: RBAC + JWT
- **包管理**: uv (后端) + pnpm (前端)

### 1.3 核心功能

1. **AIGC对话式内容生成**: 教师通过自然语言对话生成思政案例
2. **案例库管理**: 存储、检索、分类管理思政案例
3. **课程资源整合**: 整合课程体系、微课素材、虚拟仿真资源
4. **智能推荐系统**: 基于教学内容推荐相关案例
5. **案例评价与优化**: 教师对生成内容进行评价和迭代优化
6. **权限管理**: 基于RBAC的细粒度权限控制

---

## 二、系统架构设计

### 2.1 目录结构规划

基于现有vue-fastapi-admin项目架构，扩展以下模块：

```
AI-IDEological
├── app
│   ├── api
│   │   └── v1
│   │       ├── aigc/              # AIGC相关接口(新增)
│   │       │   ├── __init__.py
│   │       │   ├── chat.py        # 对话接口
│   │       │   └── generation.py  # 内容生成接口
│   │       ├── apis/              # 原有API接口
│   │       ├── base/              # 原有基础接口
│   │       ├── cases/             # 案例管理接口(新增)
│   │       │   ├── __init__.py
│   │       │   ├── cases.py       # 案例CRUD
│   │       │   ├── categories.py  # 案例分类
│   │       │   └── evaluation.py  # 案例评价
│   │       ├── courses/           # 课程管理接口(新增)
│   │       │   ├── __init__.py
│   │       │   ├── courses.py     # 课程管理
│   │       │   └── resources.py   # 教学资源
│   │       ├── menus/             # 原有菜单接口
│   │       ├── roles/             # 原有角色接口
│   │       └── users/             # 原有用户接口
│   ├── controllers/
│   │   ├── aigc_controller.py     # AIGC控制器(新增)
│   │   ├── case_controller.py     # 案例控制器(新增)
│   │   └── course_controller.py   # 课程控制器(新增)
│   ├── core/
│   │   ├── aigc/                  # AIGC核心模块(新增)
│   │   │   ├── __init__.py
│   │   │   ├── prompt_template.py # 提示词模板
│   │   │   ├── llm_service.py     # LLM服务封装
│   │   │   ├── content_parser.py  # 内容解析器
│   │   │   └── stream_handler.py  # 流式输出处理
│   │   ├── init_app.py            # 原有应用初始化
│   │   └── security.py            # 原有安全模块
│   ├── log/                       # 原有日志目录
│   ├── models/
│   │   ├── case.py                # 案例模型(新增)
│   │   ├── category.py            # 分类模型(新增)
│   │   ├── course.py              # 课程模型(新增)
│   │   ├── evaluation.py          # 评价模型(新增)
│   │   ├── resource.py            # 资源模型(新增)
│   │   ├── chat_history.py        # 对话历史模型(新增)
│   │   ├── user.py                # 原有用户模型
│   │   ├── role.py                # 原有角色模型
│   │   └── menu.py                # 原有菜单模型
│   ├── schemas/
│   │   ├── aigc.py                # AIGC请求响应模式(新增)
│   │   ├── case.py                # 案例模式(新增)
│   │   ├── course.py              # 课程模式(新增)
│   │   └── evaluation.py          # 评价模式(新增)
│   ├── settings/
│   │   └── config.py              # 配置文件(需扩展AIGC配置)
│   └── utils/
│       └── aigc_utils.py          # AIGC工具类(新增)
├── deploy/                        # 原有部署目录
├── web/
│   ├── build/                     # 原有构建配置
│   ├── public/                    # 原有公共资源
│   ├── settings/                  # 原有前端配置
│   └── src/
│       ├── api/
│       │   ├── aigc.js            # AIGC API(新增)
│       │   ├── case.js            # 案例API(新增)
│       │   └── course.js          # 课程API(新增)
│       ├── assets/                # 原有静态资源
│       ├── components/
│       │   ├── aigc/              # AIGC组件(新增)
│       │   │   ├── ChatDialog.vue     # 对话组件
│       │   │   ├── CaseCard.vue       # 案例卡片
│       │   │   ├── PromptEditor.vue   # 提示词编辑器
│       │   │   └── StreamOutput.vue   # 流式输出组件
│       │   ├── common/            # 原有通用组件
│       │   ├── icon/              # 原有图标组件
│       │   ├── page/              # 原有页面组件
│       │   ├── query-bar/         # 原有查询栏
│       │   └── table/             # 原有表格组件
│       ├── composables/           # 原有可组合式功能
│       ├── directives/            # 原有指令
│       ├── layout/                # 原有布局
│       ├── router/
│       │   ├── guard/             # 原有路由守卫
│       │   └── routes/
│       │       └── modules/
│       │           ├── aigc.js    # AIGC路由(新增)
│       │           ├── case.js    # 案例路由(新增)
│       │           └── course.js  # 课程路由(新增)
│       ├── store/
│       │   └── modules/
│       │       ├── aigc.js        # AIGC状态(新增)
│       │       └── case.js        # 案例状态(新增)
│       ├── styles/                # 原有样式
│       ├── utils/                 # 原有工具类
│       └── views/
│           ├── aigc/              # AIGC视图(新增)
│           │   ├── chat.vue       # 对话页面
│           │   └── generation.vue # 生成页面
│           ├── case/              # 案例管理视图(新增)
│           │   ├── list.vue       # 案例列表
│           │   ├── detail.vue     # 案例详情
│           │   └── category.vue   # 分类管理
│           ├── course/            # 课程管理视图(新增)
│           │   ├── list.vue       # 课程列表
│           │   └── resource.vue   # 资源管理
│           ├── error-page/        # 原有错误页面
│           ├── login/             # 原有登录页面
│           ├── profile/           # 原有个人资料
│           ├── system/            # 原有系统管理
│           └── workbench/         # 原有工作台
├── requirements.txt               # Python依赖(需更新)
├── pyproject.toml                 # uv配置(需更新)
├── README.md                      # 项目说明
└── AI-IDEological项目实施方案.md   # 本文档
```

### 2.2 数据库设计

#### 2.2.1 核心表结构

**Course - 课程表**
```python
class Course(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, description="课程名称")
    code = fields.CharField(max_length=50, unique=True, description="课程代码")
    description = fields.TextField(null=True, description="课程描述")
    syllabus = fields.JSONField(null=True, description="课程大纲")
    created_by = fields.ForeignKeyField('models.User', related_name='created_courses')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "courses"
```

**Category - 案例分类表**
```python
class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="分类名称")
    description = fields.TextField(null=True, description="分类描述")
    parent = fields.ForeignKeyField('models.Category', null=True, related_name='children')
    sort_order = fields.IntField(default=0, description="排序")
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "categories"
```

**Case - 思政案例表**
```python
class Case(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=500, description="案例标题")
    content = fields.TextField(description="案例内容")
    summary = fields.CharField(max_length=500, null=True, description="案例摘要")
    course = fields.ForeignKeyField('models.Course', related_name='cases')
    category = fields.ForeignKeyField('models.Category', related_name='cases')
    source = fields.CharField(max_length=20, description="来源: manual/aigc")
    keywords = fields.JSONField(default=list, description="关键词")
    knowledge_points = fields.JSONField(default=list, description="知识点")
    ideology_themes = fields.JSONField(default=list, description="思政主题")
    difficulty_level = fields.IntField(default=3, description="难度等级1-5")
    usage_count = fields.IntField(default=0, description="使用次数")
    avg_rating = fields.FloatField(default=0, description="平均评分")
    ai_metadata = fields.JSONField(null=True, description="AI生成元数据")
    created_by = fields.ForeignKeyField('models.User', related_name='created_cases')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "cases"
```

**Resource - 教学资源表**
```python
class Resource(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=300, description="资源标题")
    type = fields.CharField(max_length=50, description="类型: video/document/simulation/image")
    file_path = fields.CharField(max_length=500, description="文件路径")
    file_size = fields.BigIntField(default=0, description="文件大小(字节)")
    duration = fields.IntField(null=True, description="时长(秒,视频用)")
    course = fields.ForeignKeyField('models.Course', related_name='resources')
    case = fields.ForeignKeyField('models.Case', null=True, related_name='resources')
    tags = fields.JSONField(default=list, description="标签")
    metadata = fields.JSONField(default=dict, description="元数据")
    created_by = fields.ForeignKeyField('models.User', related_name='uploaded_resources')
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "resources"
```

**Evaluation - 案例评价表**
```python
class Evaluation(Model):
    id = fields.IntField(pk=True)
    case = fields.ForeignKeyField('models.Case', related_name='evaluations')
    rating = fields.IntField(description="评分1-5")
    comment = fields.TextField(null=True, description="评价内容")
    usefulness = fields.IntField(null=True, description="实用性1-5")
    relevance = fields.IntField(null=True, description="相关性1-5")
    clarity = fields.IntField(null=True, description="清晰度1-5")
    evaluated_by = fields.ForeignKeyField('models.User', related_name='evaluations')
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "evaluations"
```

**ChatHistory - 对话历史表**
```python
class ChatHistory(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='chat_histories')
    session_id = fields.CharField(max_length=100, description="会话ID")
    messages = fields.JSONField(default=list, description="对话消息列表")
    context = fields.JSONField(null=True, description="上下文信息")
    generated_case_ids = fields.JSONField(default=list, description="生成的案例ID列表")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "chat_histories"
```

### 2.3 API接口设计

#### 2.3.1 AIGC接口

**POST /api/v1/aigc/chat**
- 功能: 对话式生成思政案例
- 请求体:
```json
{
  "message": "请为软件工程敏捷开发章节生成一个关于团队协作的思政案例",
  "session_id": "uuid",
  "context": {
    "course_id": 1,
    "chapter": "敏捷开发",
    "knowledge_points": ["Scrum", "Sprint"]
  }
}
```
- 响应:
```json
{
  "session_id": "uuid",
  "reply": "AI回复内容",
  "case_preview": {
    "title": "案例标题",
    "summary": "案例摘要"
  }
}
```

**POST /api/v1/aigc/generate**
- 功能: 直接生成完整案例
- 请求体:
```json
{
  "course_id": 1,
  "chapter": "软件测试",
  "knowledge_points": ["单元测试", "集成测试"],
  "ideology_theme": "质量意识",
  "requirements": {
    "length": "medium",
    "difficulty": 3,
    "style": "案例分析"
  }
}
```

**GET /api/v1/aigc/stream**
- 功能: 流式输出生成结果
- 参数: session_id
- 响应: Server-Sent Events (SSE)

#### 2.3.2 案例管理接口

**GET /api/v1/cases**
- 功能: 获取案例列表
- 参数: page, size, course_id, category_id, source, keyword

**POST /api/v1/cases**
- 功能: 创建案例

**GET /api/v1/cases/{id}**
- 功能: 获取案例详情

**PUT /api/v1/cases/{id}**
- 功能: 更新案例

**DELETE /api/v1/cases/{id}**
- 功能: 删除案例

**POST /api/v1/cases/{id}/evaluate**
- 功能: 评价案例

**GET /api/v1/cases/recommend**
- 功能: 推荐相关案例
- 参数: course_id, case_id

#### 2.3.3 课程管理接口

**GET /api/v1/courses**
**POST /api/v1/courses**
**GET /api/v1/courses/{id}**
**PUT /api/v1/courses/{id}**
**DELETE /api/v1/courses/{id}**

**POST /api/v1/courses/{id}/resources**
- 功能: 上传教学资源

**GET /api/v1/courses/{id}/statistics**
- 功能: 获取课程统计数据

---

## 三、实施步骤

### 阶段一: 基础架构搭建 (第1-2周)

#### 任务清单

**1. 环境配置与依赖安装**

更新 `pyproject.toml`:
```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "tortoise-orm>=0.20.0",
    "aerich>=0.7.2",
    "openai>=1.0.0",           # 新增
    "anthropic>=0.7.0",        # 新增(可选)
    "tiktoken>=0.5.0",         # 新增
    "redis>=5.0.0",            # 新增
    "celery>=5.3.0",           # 新增
    "python-multipart>=0.0.6",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose>=3.3.0",
    "passlib>=1.7.4",
    "aiosqlite>=0.19.0"
]
```

安装依赖:
```bash
# 激活虚拟环境
.\.venv\Scripts\activate  # Windows

# 使用uv安装新依赖
uv pip install openai anthropic tiktoken redis celery
```

**2. 配置文件扩展**

修改 `app/settings/config.py`:
```python
class Settings(BaseSettings):
    # ... 原有配置 ...
    
    # AIGC配置
    AIGC_PROVIDER: str = "openai"  # openai/azure/qwen/wenxin
    AIGC_API_KEY: str = ""
    AIGC_API_BASE: str = "https://api.openai.com/v1"
    AIGC_MODEL: str = "gpt-4"
    AIGC_MAX_TOKENS: int = 2000
    AIGC_TEMPERATURE: float = 0.7
    AIGC_TIMEOUT: int = 60
    
    # 向量化配置(可选,用于案例检索)
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    
    # Redis配置(用于缓存和任务队列)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # 文件上传配置
    UPLOAD_DIR: str = f"{BASE_DIR}/uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".mp4", ".avi"]
```

**3. 创建数据模型**

创建 `app/models/course.py`:
```python
from tortoise import fields
from tortoise.models import Model

class Course(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, description="课程名称")
    code = fields.CharField(max_length=50, unique=True, description="课程代码")
    description = fields.TextField(null=True, description="课程描述")
    syllabus = fields.JSONField(null=True, description="课程大纲")
    created_by = fields.ForeignKeyField('models.User', related_name='created_courses')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "courses"
        table_description = "课程表"
```

创建 `app/models/category.py`:
```python
from tortoise import fields
from tortoise.models import Model

class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="分类名称")
    description = fields.TextField(null=True, description="分类描述")
    parent = fields.ForeignKeyField('models.Category', null=True, related_name='children')
    sort_order = fields.IntField(default=0, description="排序")
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "categories"
        table_description = "案例分类表"
```

创建 `app/models/case.py`:
```python
from tortoise import fields
from tortoise.models import Model

class Case(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=500, description="案例标题")
    content = fields.TextField(description="案例内容")
    summary = fields.CharField(max_length=500, null=True, description="案例摘要")
    course = fields.ForeignKeyField('models.Course', related_name='cases')
    category = fields.ForeignKeyField('models.Category', related_name='cases')
    source = fields.CharField(max_length=20, description="来源: manual/aigc")
    keywords = fields.JSONField(default=list, description="关键词")
    knowledge_points = fields.JSONField(default=list, description="知识点")
    ideology_themes = fields.JSONField(default=list, description="思政主题")
    difficulty_level = fields.IntField(default=3, description="难度等级1-5")
    usage_count = fields.IntField(default=0, description="使用次数")
    avg_rating = fields.FloatField(default=0, description="平均评分")
    ai_metadata = fields.JSONField(null=True, description="AI生成元数据")
    created_by = fields.ForeignKeyField('models.User', related_name='created_cases')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "cases"
        table_description = "思政案例表"
```

创建 `app/models/evaluation.py`:
```python
from tortoise import fields
from tortoise.models import Model

class Evaluation(Model):
    id = fields.IntField(pk=True)
    case = fields.ForeignKeyField('models.Case', related_name='evaluations')
    rating = fields.IntField(description="评分1-5")
    comment = fields.TextField(null=True, description="评价内容")
    usefulness = fields.IntField(null=True, description="实用性1-5")
    relevance = fields.IntField(null=True, description="相关性1-5")
    clarity = fields.IntField(null=True, description="清晰度1-5")
    evaluated_by = fields.ForeignKeyField('models.User', related_name='evaluations')
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "evaluations"
        table_description = "案例评价表"
```

创建 `app/models/chat_history.py`:
```python
from tortoise import fields
from tortoise.models import Model

class ChatHistory(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='chat_histories')
    session_id = fields.CharField(max_length=100, description="会话ID")
    messages = fields.JSONField(default=list, description="对话消息列表")
    context = fields.JSONField(null=True, description="上下文信息")
    generated_case_ids = fields.JSONField(default=list, description="生成的案例ID列表")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "chat_histories"
        table_description = "对话历史表"
```

**4. 数据库迁移**

修改 `app/settings/config.py` 中的 TORTOISE_ORM 配置:
```python
TORTOISE_ORM: dict = {
    "connections": {
        "sqlite": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": f"{BASE_DIR}/db.sqlite3"},
        },
    },
    "apps": {
        "models": {
            "models": [
                "app.models",           # 原有模型
                "app.models.course",    # 新增
                "app.models.category",  # 新增
                "app.models.case",      # 新增
                "app.models.evaluation",# 新增
                "app.models.chat_history", # 新增
                "aerich.models"
            ],
            "default_connection": "sqlite",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
```

执行迁移:
```bash
# 初始化aerich(如果还未初始化)
aerich init -t app.settings.config.TORTOISE_ORM

# 生成迁移文件
aerich migrate --name "add_aigc_models"

# 执行迁移
aerich upgrade
```

**5. 创建Pydantic Schemas**

创建 `app/schemas/course.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    name: str = Field(..., description="课程名称")
    code: str = Field(..., description="课程代码")
    description: Optional[str] = Field(None, description="课程描述")
    syllabus: Optional[dict] = Field(None, description="课程大纲")

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    syllabus: Optional[dict] = None

class CourseOut(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

创建 `app/schemas/case.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CaseBase(BaseModel):
    title: str = Field(..., max_length=500)
    content: str
    summary: Optional[str] = Field(None, max_length=500)
    course_id: int
    category_id: int
    keywords: List[str] = Field(default_factory=list)
    knowledge_points: List[str] = Field(default_factory=list)
    ideology_themes: List[str] = Field(default_factory=list)
    difficulty_level: int = Field(default=3, ge=1, le=5)

class CaseCreate(CaseBase):
    source: str = Field(default="manual")

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category_id: Optional[int] = None
    keywords: Optional[List[str]] = None
    knowledge_points: Optional[List[str]] = None
    ideology_themes: Optional[List[str]] = None
    difficulty_level: Optional[int] = None

class CaseOut(CaseBase):
    id: int
    source: str
    usage_count: int
    avg_rating: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

创建 `app/schemas/aigc.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[Dict] = Field(None, description="上下文信息")

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    case_preview: Optional[Dict] = None

class GenerationRequest(BaseModel):
    course_id: int
    chapter: str
    knowledge_points: List[str]
    ideology_theme: str
    requirements: Optional[Dict] = Field(default_factory=dict)

class GenerationResponse(BaseModel):
    case_id: int
    title: str
    content: str
    metadata: Dict
```

---

### 阶段二: AIGC核心功能开发 (第3-4周)

#### 任务清单

**1. LLM服务封装**

创建 `app/core/aigc/llm_service.py`:
```python
from openai import AsyncOpenAI
from app.settings.config import settings
from typing import List, Dict, Optional, AsyncGenerator
import json

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.AIGC_API_KEY,
            base_url=settings.AIGC_API_BASE,
            timeout=settings.AIGC_TIMEOUT
        )
    
    async def generate_case(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """生成思政案例"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=settings.AIGC_MODEL,
            messages=messages,
            max_tokens=settings.AIGC_MAX_TOKENS,
            temperature=settings.AIGC_TEMPERATURE
        )
        
        return response.choices[0].message.content
    
    async def generate_case_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成思政案例"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=settings.AIGC_MODEL,
            messages=messages,
            max_tokens=settings.AIGC_MAX_TOKENS,
            temperature=settings.AIGC_TEMPERATURE,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """多轮对话"""
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        response = await self.client.chat.completions.create(
            model=settings.AIGC_MODEL,
            messages=messages,
            max_tokens=settings.AIGC_MAX_TOKENS,
            temperature=settings.AIGC_TEMPERATURE
        )
        
        return response.choices[0].message.content
    
    async def parse_structured_output(self, content: str) -> Dict:
        """解析结构化输出"""
        try:
            # 尝试提取JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # 如果无法解析为JSON,返回原始内容
        return {"content": content}
```

**2. 提示词模板设计**

创建 `app/core/aigc/prompt_template.py`:
```python
from typing import Dict, List

class PromptTemplate:
    
    SYSTEM_PROMPT = """你是一位资深的软件工程教育专家,擅长将技术知识与课程思政深度融合。
你的任务是根据教师提供的教学内容,生成高质量的思政案例。

生成案例时请遵循以下原则:
1. 案例必须紧密结合软件工程实践,避免脱离技术内容
2. 思政元素融入要自然,不生硬,能引发学生思考
3. 案例应具有真实性和时代性,最好来源于实际项目
4. 案例长度适中(500-1000字),结构清晰
5. 案例应包含:背景介绍、技术挑战、解决方案、思政启示
6. 思政主题可包括:职业道德、团队协作、质量意识、创新精神、社会责任等
"""

    CASE_GENERATION_TEMPLATE = """请基于以下软件工程教学内容生成一个课程思政案例:

【课程信息】
课程名称: {course_name}
章节名称: {chapter}

【教学内容】
知识点: {knowledge_points}
技术要点: {technical_points}

【思政要求】
思政主题: {ideology_theme}
融入方式: {integration_style}

【案例要求】
难度等级: {difficulty_level}/5
案例长度: {length}
目标受众: {target_audience}

请生成一个符合以上要求的思政案例,并以JSON格式输出:
{{
    "title": "案例标题",
    "background": "背景介绍(150-200字)",
    "technical_challenge": "技术挑战描述",
    "solution": "解决方案",
    "ideology_insight": "思政启示(重点部分)",
    "discussion_questions": ["讨论问题1", "讨论问题2", "讨论问题3"],
    "keywords": ["关键词1", "关键词2"],
    "references": ["参考资料1", "参考资料2"]
}}
"""

    CHAT_TEMPLATE = """基于之前的对话,继续帮助教师完善思政案例。

对话历史:
{chat_history}

当前教师需求:
{current_message}

请提供具体建议或生成相应内容。"""

    CASE_OPTIMIZATION_TEMPLATE = """请优化以下思政案例:

【原案例】
{original_case}

【优化要求】
{optimization_requirements}

请提供优化后的版本,保持JSON格式输出。"""

    @classmethod
    def build_generation_prompt(cls, **kwargs) -> str:
        """构建生成案例的提示词"""
        # 设置默认值
        defaults = {
            "course_name": "软件工程",
            "chapter": "未指定",
            "knowledge_points": "未指定",
            "technical_points": "未指定",
            "ideology_theme": "职业道德",
            "integration_style": "自然融入",
            "difficulty_level": 3,
            "length": "中等(500-800字)",
            "target_audience": "本科生"
        }
        defaults.update(kwargs)
        
        return cls.CASE_GENERATION_TEMPLATE.format(**defaults)
    
    @classmethod
    def build_chat_prompt(cls, chat_history: List[Dict], current_message: str) -> str:
        """构建对话提示词"""
        history_text = "\n".join([
            f"{'教师' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
            for msg in chat_history[-5:]  # 只保留最近5轮对话
        ])
        
        return cls.CHAT_TEMPLATE.format(
            chat_history=history_text,
            current_message=current_message
        )
    
    @classmethod
    def build_optimization_prompt(cls, original_case: str, requirements: str) -> str:
        """构建优化提示词"""
        return cls.CASE_OPTIMIZATION_TEMPLATE.format(
            original_case=original_case,
            optimization_requirements=requirements
        )
```

**3. 内容解析器**

创建 `app/core/aigc/content_parser.py`:
```python
import json
import re
from typing import Dict, Optional

class ContentParser:
    
    @staticmethod
    def extract_json(content: str) -> Optional[Dict]:
        """从文本中提取JSON"""
        try:
            # 方法1: 直接解析
            return json.loads(content)
        except:
            pass
        
        try:
            # 方法2: 提取JSON代码块
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except:
            pass
        
        try:
            # 方法3: 查找第一个完整的JSON对象
            start = content.find('{')
            if start != -1:
                #