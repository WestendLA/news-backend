
from utils.cache import get_json_cache


CATEGORIES_KEY = "news:categories"


async def get_categories():
    """获取新闻分类。"""
    categories = await get_json_cache(CATEGORIES_KEY)
    if categories:
        return categories
    return None

async def set_categories(categories: list):
    """设置新闻分类。"""
    await set_cache(CATEGORIES_KEY, categories)