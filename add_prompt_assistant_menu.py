#!/usr/bin/env python3
"""
添加提示词助手菜单到数据库
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tortoise import Tortoise
from app.models.admin import Menu, Role
from app.schemas.menus import MenuType

async def add_prompt_assistant_menu():
    await Tortoise.init(
        db_url='mysql://root:12345678@localhost:3306/AIdata',
        modules={'models': ['app.models.admin', 'app.models.ideological']}
    )

    try:
        # 查找"课程思政"父菜单
        aigc_menu = await Menu.filter(name="课程思政").first()

        if not aigc_menu:
            print("❌ 未找到'课程思政'父菜单")
            return

        print(f"✅ 找到课程思政父菜单 (ID: {aigc_menu.id})")

        # 检查是否已经存在提示词助手菜单
        existing_menu = await Menu.filter(name="提示词助手", parent_id=aigc_menu.id).first()

        if existing_menu:
            print("ℹ️  提示词助手菜单已存在，跳过添加")
            return

        # 创建提示词助手菜单
        prompt_assistant_menu = await Menu.create(
            name="提示词助手",
            menu_type=MenuType.MENU,
            icon="mdi:robot-outline",
            path="prompt-assistant",
            order=5,  # 放在"教学资源"后面
            parent_id=aigc_menu.id,
            is_hidden=False,
            component="/aigc/prompt-assistant",
            keepalive=False,
            redirect=None
        )

        print(f"✅ 成功创建提示词助手菜单 (ID: {prompt_assistant_menu.id})")

        # 分配给所有角色
        roles = await Role.all()
        for role in roles:
            await role.menus.add(prompt_assistant_menu)

        print(f"✅ 已将菜单分配给 {len(roles)} 个角色")

    except Exception as e:
        print(f"❌ 添加菜单失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    print("🔧 开始添加提示词助手菜单...")
    asyncio.run(add_prompt_assistant_menu())
    print("🎉 完成！")