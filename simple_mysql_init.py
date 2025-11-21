#!/usr/bin/env python3
"""
简化的MySQL数据库初始化脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def init_database():
    """初始化MySQL数据库"""
    try:
        print("🔗 开始初始化MySQL数据库...")

        # 确保能正确导入模块
        import os
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.config")

        # 直接使用Tortoise ORM，避免复杂的导入
        from tortoise import Tortoise

        # 数据库配置
        db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'AIdata'
        }

        print(f"📊 连接MySQL数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")

        # 初始化数据库连接
        await Tortoise.init(
            db_url=f"mysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
            modules={'models': ['app.models.admin', 'app.models.ideological']}
        )

        # 生成数据库表
        print("🏗️  正在生成数据库表...")
        await Tortoise.generate_schemas()
        print("✅ 数据库表生成完成！")

        # 创建默认管理员用户
        from app.models.admin import User
        from app.utils.password import get_password_hash

        admin_exists = await User.filter(username="admin").exists()
        if not admin_exists:
            # 使用系统的密码哈希方法
            password = "123456"
            hashed_password = get_password_hash(password)

            await User.create(
                username="admin",
                alias="系统管理员",
                email="admin@example.com",
                password=hashed_password,
                is_superuser=True,
                is_active=True
            )
            print("✅ 默认管理员用户创建成功！")
            print("   用户名: admin")
            print("   密码: 123456")
        else:
            print("ℹ️  管理员用户已存在")

        # 创建默认菜单
        from app.models.admin import Menu, Role
        from app.schemas.menus import MenuType

        menus_count = await Menu.all().count()
        if menus_count == 0:
            print("📋 正在创建默认菜单...")

            # 系统管理父菜单
            parent_menu = await Menu.create(
                menu_type=MenuType.CATALOG,
                name="系统管理",
                path="/system",
                order=1,
                parent_id=0,
                icon="carbon:gui-management",
                is_hidden=False,
                component="Layout",
                keepalive=False,
                redirect="/system/user",
            )

            # 系统管理子菜单
            children_menu = [
                Menu(
                    menu_type=MenuType.MENU,
                    name="用户管理",
                    path="user",
                    order=1,
                    parent_id=parent_menu.id,
                    icon="material-symbols:person-outline-rounded",
                    is_hidden=False,
                    component="/system/user",
                    keepalive=False,
                ),
                Menu(
                    menu_type=MenuType.MENU,
                    name="角色管理",
                    path="role",
                    order=2,
                    parent_id=parent_menu.id,
                    icon="carbon:user-role",
                    is_hidden=False,
                    component="/system/role",
                    keepalive=False,
                ),
            ]

            await Menu.bulk_create(children_menu)

            # AIGC相关菜单
            aigc_menu = await Menu.create(
                menu_type=MenuType.CATALOG,
                name="课程思政",
                path="/aigc",
                order=2,
                parent_id=0,
                icon="mdi:school-outline",
                is_hidden=False,
                component="Layout",
                keepalive=False,
                redirect="/aigc/chat",
            )

            aigc_children = [
                Menu(
                    menu_type=MenuType.MENU,
                    name="AIGC对话",
                    path="chat",
                    order=1,
                    parent_id=aigc_menu.id,
                    icon="mdi:chat-outline",
                    is_hidden=False,
                    component="/aigc/chat",
                    keepalive=False,
                ),
                Menu(
                    menu_type=MenuType.MENU,
                    name="案例库",
                    path="cases",
                    order=2,
                    parent_id=aigc_menu.id,
                    icon="mdi:book-outline",
                    is_hidden=False,
                    component="/aigc/cases",
                    keepalive=False,
                ),
                Menu(
                    menu_type=MenuType.MENU,
                    name="提示词模板",
                    path="prompts",
                    order=3,
                    parent_id=aigc_menu.id,
                    icon="mdi:file-document-outline",
                    is_hidden=False,
                    component="/aigc/prompts",
                    keepalive=False,
                ),
                Menu(
                    menu_type=MenuType.MENU,
                    name="教学资源",
                    path="resources",
                    order=4,
                    parent_id=aigc_menu.id,
                    icon="mdi:folder-outline",
                    is_hidden=False,
                    component="/aigc/resources",
                    keepalive=False,
                ),
            ]

            await Menu.bulk_create(aigc_children)
            print("✅ 默认菜单创建完成")

        # 创建角色
        roles_count = await Role.all().count()
        if roles_count == 0:
            print("🔐 正在创建默认角色...")

            admin_role = await Role.create(
                name="管理员",
                desc="管理员角色，拥有所有权限",
            )
            user_role = await Role.create(
                name="教师",
                desc="教师角色，拥有AIGC相关权限",
            )

            # 分配菜单权限
            all_menus = await Menu.all()
            await admin_role.menus.add(*all_menus)
            await user_role.menus.add(*all_menus)

            print("✅ 角色和权限创建完成")

        await Tortoise.close_connections()

        print("\n🎉 MySQL数据库初始化完成！")
        print("\n下一步：")
        print("1. 启动后端服务: python run.py")
        print("2. 启动前端服务: cd web && pnpm dev")
        print("3. 访问系统: http://localhost:3000")
        print("   用户名: admin, 密码: 123456")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

        print("\n💡 请检查以下配置:")
        print("1. 确保MySQL服务已启动")
        print("2. 确保数据库 'AIdata' 已创建")
        print("3. 确保MySQL用户权限正确")
        print("4. 确保Python依赖已安装:")
        print("   pip install pymysql aiomysql tortoise-orm")

        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI-IDEological MySQL 数据库初始化工具")
    print("=" * 60)

    # 简单的依赖检查
    try:
        import pymysql
        print("✅ pymysql 已安装")
    except ImportError:
        print("❌ pymysql 未安装")
        print("正在安装依赖...")
        os.system("pip install pymysql aiomysql tortoise-orm passlib")

    print("\n⚠️  初始化前请确保:")
    print("1. MySQL服务已启动")
    print("2. 已创建数据库 'AIdata'")
    print("3. MySQL用户权限正确配置")
    print()

    try:
        input("按回车键继续初始化...")
    except KeyboardInterrupt:
        print("\n初始化已取消")
        sys.exit(0)

    asyncio.run(init_database())