"""
系统初始化数据脚本
用于创建默认的系统提示词模板
"""

import asyncio
import logging
from tortoise import Tortoise
from app.models.ideological import PromptTemplate, PromptAssistantTemplate
from app.models.admin import User
from .init_prompt_assistant_data import init_prompt_assistant_templates

logger = logging.getLogger(__name__)

# 默认系统提示词模板数据
DEFAULT_TEMPLATES = [
    {
        "name": "软件工程课程思政案例生成模板",
        "description": "生成结合软件工程专业知识的课程思政教学案例",
        "template_type": "case_generation",
        "template_content": """请基于以下要求生成一个软件工程课程思政教学案例：

**软件工程章节：** {{软件工程章节}}
**思政主题：** {{思政主题}}
**案例类型：** {{案例类型}}
**难度等级：** {{难度等级}}

**具体要求：**
1. 案例背景：描述一个真实的软件工程项目或技术场景
2. 技术知识点：融入{{技术知识点}}等核心技术内容
3. 思政元素：体现{{思政主题}}的核心价值，如职业道德、工匠精神、创新精神等
4. 案例分析：深入分析技术选择背后的价值考量
5. 教学启示：提炼可推广的教学价值和育人意义
6. 讨论思考：设计3-5个引导学生深入思考的问题

请确保案例既有技术深度，又有人文温度，能够启发学生对技术发展的全面思考。""",
        "variables": ["软件工程章节", "思政主题", "案例类型", "难度等级", "技术知识点"],
        "category": "思政案例",
        "software_engineering_chapter": "软件工程概述",
        "ideological_theme": "工匠精神",
        "is_system": True,
        "is_active": True,
    },
    {
        "name": "软件工程讨论题生成模板",
        "description": "生成启发性的软件工程课程思政讨论题",
        "template_type": "discussion_generation",
        "template_content": """请基于软件工程课程思政要求，设计一组具有启发性的讨论题：

**教学章节：** {{教学章节}}
**思政主题：** {{思政主题}}
**讨论时长：** {{讨论时长}}
**参与人数：** {{参与人数}}

**设计要求：**
1. 围绕{{核心技术概念}}展开讨论
2. 融入{{思政主题}}的价值引领
3. 设计{{问题数量}}个层次递进的问题：
   - 基础层：技术与伦理的基本认知
   - 分析层：案例背后的价值权衡
   - 应用层：实践中的决策选择
   - 升华层：对未来发展的思考
4. 每个问题都要引导学生进行价值判断和伦理思考
5. 提供讨论要点和引导方向

请确保讨论题既有理论深度，又有实践指导意义。""",
        "variables": ["教学章节", "思政主题", "讨论时长", "参与人数", "核心技术概念", "问题数量"],
        "category": "讨论题",
        "software_engineering_chapter": "需求分析",
        "ideological_theme": "职业伦理",
        "is_system": True,
        "is_active": True,
    },
    {
        "name": "软件工程知识点思政融入模板",
        "description": "将思政元素融入软件工程知识点的讲解",
        "template_type": "knowledge_point",
        "template_content": """请为以下软件工程知识点设计思政融入方案：

**知识点：** {{知识点}}
**软件工程章节：** {{章节}}
**思政融入点：** {{思政主题}}
**教学目标：** {{教学目标}}

**设计要求：**
1. 知识点解析：清晰阐述{{知识点}}的技术内涵
2. 思政切入点：找到技术与思政的自然结合点
3. 融入方式：
   - 案例导入：选择{{案例类型}}作为教学案例
   - 价值引导：强调{{核心价值}}的重要性
   - 实践结合：联系{{实践场景}}的实际应用
4. 教学建议：提供3-5条具体的教学建议
5. 评价方式：设计知识与价值观的综合评价方法

要求思政融入自然不生硬，实现知识传授与价值引领的有机统一。""",
        "variables": ["知识点", "章节", "思政主题", "教学目标", "案例类型", "核心价值", "实践场景"],
        "category": "知识点讲解",
        "software_engineering_chapter": "软件设计",
        "ideological_theme": "科学精神",
        "is_system": True,
        "is_active": True,
    },
    {
        "name": "软件工程教学设计模板",
        "description": "设计完整的软件工程课程思政教学方案",
        "template_type": "teaching_design",
        "template_content": """请设计一个完整的软件工程课程思政教学方案：

**课程主题：** {{课程主题}}
**软件工程章节：** {{章节}}
**思政主题：** {{思政主题}}
**课时安排：** {{课时安排}}
**学生层次：** {{学生层次}}

**设计方案要求：**

## 一、教学目标
- 知识目标：{{知识目标}}
- 能力目标：{{能力目标}}
- 思政目标：{{思政目标}}

## 二、教学重难点
- 教学重点：{{教学重点}}
- 教学难点：{{教学难点}}
- 思政融入点：{{思政融入点}}

## 三、教学过程
1. 导入环节（{{导入时长}}分钟）
   - 创设{{导入情境}}
   - 引入思政元素{{导入思政}}

2. 新知讲授（{{讲授时长}}分钟）
   - {{核心知识点1}}讲解
   - {{核心知识点2}}讲解
   - 思政自然融入

3. 案例分析（{{案例时长}}分钟）
   - 分析{{典型案例}}
   - 思政价值讨论

4. 实践环节（{{实践时长}}分钟）
   - {{实践活动设计}}
   - 价值观体验

## 四、教学评价
- 知识掌握评价：{{知识评价方式}}
- 价值引领评价：{{价值评价方式}}

## 五、教学反思
- 预期效果：{{预期效果}}
- 可能问题：{{可能问题}}

请确保教学设计科学合理，思政融入自然有效。""",
        "variables": [
            "课程主题", "章节", "思政主题", "课时安排", "学生层次",
            "知识目标", "能力目标", "思政目标", "教学重点", "教学难点",
            "思政融入点", "导入时长", "导入情境", "导入思政",
            "讲授时长", "核心知识点1", "核心知识点2", "案例时长",
            "典型案例", "实践时长", "实践活动设计", "知识评价方式",
            "价值评价方式", "预期效果", "可能问题"
        ],
        "category": "教学设计",
        "software_engineering_chapter": "软件测试",
        "ideological_theme": "责任担当",
        "is_system": True,
        "is_active": True,
    },
    {
        "name": "软件工程师职业道德思考题模板",
        "description": "生成软件工程师职业道德相关的思考题",
        "template_type": "thinking_generation",
        "template_content": """请基于软件工程师职业道德要求，设计一组深度思考题：

**场景背景：** {{场景背景}}
**涉及技术：** {{相关技术}}
**职业道德主题：** {{职业道德主题}}
**思考深度：** {{思考深度}}

**设计要求：**
1. 基于{{真实案例}}设计问题情境
2. 围绕以下职业道德维度：
   - 诚信正直：在{{技术场景}}中的体现
   - 专业能力：持续学习和技能提升
   - 社会责任：技术发展的社会影响
   - 团队协作：多方利益平衡
   - 创新精神：技术突破与伦理约束

3. 设计{{问题数量}}个层次递进的思考题：
   - 认知层面：识别道德困境
   - 分析层面：权衡多方利益
   - 判断层面：做出价值选择
   - 行动层面：制定解决方案
   - 反思层面：总结经验教训

4. 每个问题都要提供：
   - 思考引导
   - 关键概念
   - 实践建议

请确保思考题既有理论深度，又有实践指导价值。""",
        "variables": [
            "场景背景", "相关技术", "职业道德主题", "思考深度",
            "真实案例", "技术场景", "问题数量"
        ],
        "category": "思考题",
        "software_engineering_chapter": "软件维护",
        "ideological_theme": "诚信品质",
        "is_system": True,
        "is_active": True,
    },
    {
        "name": "软件工程内容优化模板",
        "description": "优化和完善已有的课程思政教学内容",
        "template_type": "content_optimization",
        "template_content": """请对以下软件工程课程思政内容进行优化：

**原始内容：**
{{原始内容}}

**优化目标：** {{优化目标}}
**软件工程章节：** {{章节}}
**思政主题：** {{思政主题}}
**教学对象：** {{教学对象}}

**优化要求：**
1. 内容结构优化：
   - 逻辑重构：{{逻辑改进方向}}
   - 知识整合：{{知识整合要点}}
   - 难度调节：{{难度调整策略}}

2. 思政融入优化：
   - 自然度提升：避免思政内容生硬嵌入
   - 深度挖掘：深化{{思政主题}}的内涵
   - 时效性增强：结合{{最新案例}}

3. 教学效果优化：
   - 互动性增强：设计{{互动环节}}
   - 实践性提升：加强{{实践应用}}
   - 评价多元化：完善{{评价机制}}

4. 表达形式优化：
   - 语言精炼：{{语言改进要求}}
   - 案例丰富：补充{{补充案例}}
   - 图文并茂：增加{{可视化元素}}

**优化标准：**
- 技术准确性与价值引领性的统一
- 知识系统性与思政渗透性的结合
- 理论深度与实践应用性的平衡
- 教学效果与学生接受度的提升

请提供完整的优化方案和具体改进建议。""",
        "variables": [
            "原始内容", "优化目标", "章节", "思政主题", "教学对象",
            "逻辑改进方向", "知识整合要点", "难度调整策略",
            "互动环节", "实践应用", "评价机制", "语言改进要求",
            "补充案例", "可视化元素"
        ],
        "category": "内容优化",
        "software_engineering_chapter": "项目管理",
        "ideological_theme": "团队协作",
        "is_system": True,
        "is_active": True,
    }
]

async def init_default_templates():
    """初始化默认的系统提示词模板"""
    try:
        logger.info("开始初始化默认提示词模板...")

        created_count = 0
        updated_count = 0

        for template_data in DEFAULT_TEMPLATES:
            # 检查是否已存在同名模板
            existing_template = await PromptTemplate.filter(
                name=template_data["name"],
                is_system=True
            ).first()

            if existing_template:
                # 更新现有模板
                await existing_template.update_from_dict(template_data)
                await existing_template.save()
                updated_count += 1
                logger.info(f"更新系统模板: {template_data['name']}")
            else:
                # 创建新模板
                await PromptTemplate.create(**template_data)
                created_count += 1
                logger.info(f"创建系统模板: {template_data['name']}")

        logger.info(f"提示词模板初始化完成！创建: {created_count}个，更新: {updated_count}个")

    except Exception as e:
        logger.error(f"初始化提示词模板失败: {str(e)}")
        raise

async def check_system_user():
    """检查系统用户是否存在，如果不存在则创建"""
    try:
        # 检查是否有超级管理员用户
        admin_user = await User.filter(is_superuser=True).first()

        if not admin_user:
            logger.warning("未找到超级管理员用户，请手动创建管理员账户")
            return False

        logger.info(f"系统用户检查完成，管理员: {admin_user.username}")
        return True

    except Exception as e:
        logger.error(f"检查系统用户失败: {str(e)}")
        return False

async def init_system_data():
    """初始化系统数据"""
    try:
        logger.info("开始初始化系统数据...")

        # 检查系统用户
        user_ok = await check_system_user()
        if not user_ok:
            logger.warning("系统用户检查未通过，但继续初始化其他数据")

        # 初始化默认模板
        await init_default_templates()

        # 初始化提示词助手模板
        await init_prompt_assistant_templates()

        logger.info("系统数据初始化完成！")

    except Exception as e:
        logger.error(f"系统数据初始化失败: {str(e)}")
        raise

async def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 初始化Tortoise ORM
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',  # 使用与主应用相同的数据库配置
        modules={'models': ['app.models']}
    )

    # 生成数据库schema
    await Tortoise.generate_schemas()

    # 初始化系统数据
    await init_system_data()

    # 关闭连接
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())