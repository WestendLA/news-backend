
from typing import Any, Dict, List

from utils.cache import get_json_cache, set_cache


CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news:list"


async def get_categories():
    """获取新闻分类。"""
    categories = await get_json_cache(CATEGORIES_KEY)
    return categories
 

async def set_categories(data: List[Dict[str, Any]], ex: int = 7200):
       """设置新闻分类。"""
       await set_cache(CATEGORIES_KEY, data, ex)
       return True

async def set_cache_news_list(category_id: int, page: int, size: int, news_list: List[Dict[str, Any]], ex: int = 7200):
    """设置新闻列表。"""
    category_id = category_id if category_id else "all"
    return await set_cache(f"{NEWS_LIST_PREFIX}:{category_id}:{page}:{size}", news_list, ex)

async def get_cache_news_list(category_id: int, page: int, size: int):
    """获取新闻列表。"""
    category_id = category_id if category_id else "all"
    news_list = await get_json_cache(f"{NEWS_LIST_PREFIX}:{category_id}:{page}:{size}")
    return news_list
    
