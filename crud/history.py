"""浏览历史数据访问层（CRUD）。"""
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    """添加浏览记录。"""
    history = History(user_id=user_id, news_id=news_id, view_time=datetime.now())
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


# ↓↓↓ 写 get_history_list 函数 ↓↓↓
#
# async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
#     """获取浏览历史列表（分页，含新闻详情）。
#
#     实现逻辑和收藏列表类似：
#     a) select(func.count()) 查总数
#     b) select(History, News).join(News, ...).where(...).order_by(desc(History.view_time))
#     c) 拼装数据（id, title, ..., viewTime）
#     d) hasMore 计算
#     参考 crud/favorite.py 的 get_favorite_list_crud
#     """
