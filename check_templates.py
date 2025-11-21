#!/usr/bin/env python3
"""
检查数据库中提示词模板数据的脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tortoise import Tortoise
from app.models.ideological import PromptTemplate

async def check_templates():
    await Tortoise.init(
        db_url='mysql://root:12345678@localhost:3306/AIdata',
        modules={'models': ['app.models.ideological', 'app.models.admin']}
    )

    count = await PromptTemplate.all().count()
    print(f'数据库中提示词模板数量: {count}')

    # 检查是否有系统模板
    system_count = await PromptTemplate.filter(is_system=True).count()
    print(f'系统模板数量: {system_count}')

    if count == 0:
        print('数据库中没有提示词模板数据，需要初始化')
    else:
        # 获取前几个模板看看
        templates = await PromptTemplate.all().limit(5)
        for template in templates:
            print(f'模板: {template.name} - {template.template_type} - 系统:{template.is_system}')

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(check_templates())