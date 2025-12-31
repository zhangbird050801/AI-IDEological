"""
刷新API权限脚本
用于更新数据库中的API列表，并为教师角色分配权限
"""
import asyncio
from tortoise import Tortoise
from tortoise.expressions import Q
from app.settings.config import settings
from app.controllers.api import api_controller
from app.models.admin import Api, Role


async def refresh_permissions():
    # 初始化数据库连接
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    print("🔄 开始刷新API列表...")
    await api_controller.refresh_api()
    print("✅ API列表刷新完成")
    
    # 获取教师角色
    user_role = await Role.filter(Q(name="教师") | Q(name="普通用户")).first()
    if not user_role:
        print("❌ 未找到'教师'或'普通用户'角色")
        await Tortoise.close_connections()
        return
    
    print(f"📋 找到角色: {user_role.name}")
    
    # 为教师角色分配API权限
    # 包括：所有GET请求 + 教学相关的POST/PUT/DELETE + AIGC相关的所有请求
    basic_apis = await Api.filter(
        Q(method__in=["GET"]) | 
        Q(tags__in=["基础模块", "课程管理", "章节管理", "知识点管理", 
                   "思政主题分类", "思政案例", "提示词模板", "教学资源",
                   "AIGC生成", "提示词助手"]) |
        Q(path__startswith="/api/v1/courses") |
        Q(path__startswith="/api/v1/chapters") |
        Q(path__startswith="/api/v1/knowledge-points") |
        Q(path__startswith="/api/v1/ideological") |
        Q(path__startswith="/api/v1/aigc")
    )
    
    print(f"🔑 找到 {len(basic_apis)} 个基础API")
    
    # 清除现有权限并重新分配
    await user_role.apis.clear()
    await user_role.apis.add(*basic_apis)
    
    print("✅ 权限分配完成")
    
    # 显示分配的API
    print("\n📝 已分配的API列表:")
    for api in basic_apis[:10]:  # 只显示前10个
        print(f"  - {api.method:6s} {api.path:50s} [{api.tags}]")
    if len(basic_apis) > 10:
        print(f"  ... 还有 {len(basic_apis) - 10} 个API")
    
    await Tortoise.close_connections()
    print("\n✨ 完成！请重新登录以使权限生效。")


if __name__ == "__main__":
    asyncio.run(refresh_permissions())
