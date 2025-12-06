"""
思政主题服务层
处理思政主题相关的业务逻辑，包括字符串到ID的映射
"""
from typing import Optional, Dict
from app.models.theme_category import IdeologicalThemeCategory

class ThemeService:
    """思政主题服务类"""
    
    # 缓存主题名称到ID的映射
    _theme_cache: Dict[str, int] = {}
    _cache_loaded = False
    
    @classmethod
    async def load_theme_cache(cls):
        """加载主题缓存"""
        if not cls._cache_loaded:
            categories = await IdeologicalThemeCategory.all()
            cls._theme_cache = {cat.name: cat.id for cat in categories if cat.parent_id is not None}
            cls._cache_loaded = True
    
    @classmethod
    async def get_theme_id_by_name(cls, theme_name: Optional[str]) -> Optional[int]:
        """根据主题名称获取ID"""
        if not theme_name:
            return None
        
        # 确保缓存已加载
        await cls.load_theme_cache()
        
        return cls._theme_cache.get(theme_name)
    
    @classmethod
    async def refresh_cache(cls):
        """刷新缓存"""
        cls._cache_loaded = False
        await cls.load_theme_cache()
    
    @classmethod
    async def process_form_data(cls, form_data: dict) -> dict:
        """
        处理表单数据
        现在已经完全使用外键ID，此方法保留用于向后兼容
        """
        return form_data
    
    @classmethod
    async def get_theme_name_by_id(cls, theme_id: Optional[int]) -> Optional[str]:
        """根据ID获取主题名称"""
        if not theme_id:
            return None
        
        theme = await IdeologicalThemeCategory.get_or_none(id=theme_id)
        return theme.name if theme else None
