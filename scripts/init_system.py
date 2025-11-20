#!/usr/bin/env python3
"""
系统初始化脚本
用于在首次启动时初始化数据库和默认数据
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.init_data import init_system_data
from app.core.init_app import init_app
from tortoise import Tortoise

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_database_initialized():
    """检查数据库是否已经初始化"""
    try:
        # 尝试连接数据库
        await Tortoise.init(
            db_url='sqlite://db.sqlite3',
            modules={'models': ['app.models']}
        )

        # 检查关键表是否存在
        from app.models.ideological import PromptTemplate

        template_count = await PromptTemplate.all().count()
        logger.info(f"当前数据库中有 {template_count} 个提示词模板")

        await Tortoise.close_connections()

        return template_count > 0

    except Exception as e:
        logger.error(f"检查数据库状态失败: {str(e)}")
        return False

async def create_directories():
    """创建必要的目录"""
    directories = [
        'uploads',
        'uploads/teaching_resources',
        'logs',
        'temp',
    ]

    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建目录: {dir_path}")

async def main():
    """主函数"""
    try:
        logger.info("开始系统初始化...")

        # 创建必要目录
        await create_directories()

        # 检查数据库是否已初始化
        is_initialized = await check_database_initialized()

        if is_initialized:
            logger.info("数据库已经初始化，跳过初始化步骤")
            logger.info("如需重新初始化，请删除数据库文件后重新运行此脚本")
            return

        # 初始化应用
        logger.info("正在初始化应用...")
        await init_app()

        # 初始化系统数据
        logger.info("正在初始化系统数据...")
        await init_system_data()

        logger.info("系统初始化完成！")
        logger.info("您现在可以启动应用了。")

    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())