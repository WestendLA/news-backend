"""浏览历史数据访问层（CRUD）。"""
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News
from schemas.history import HistoryItemBase, HistoryListResponse


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    """添加浏览记录（已有则更新浏览时间，无则新建）。"""
    stmt = select(History).where(
        History.user_id == user_id,
        History.news_id == news_id
    )
    result = await db.execute(stmt)
    history = result.scalars().first()

    if history:
        history.view_time = datetime.now()
    else:
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
async def get_history_list(db: AsyncSession, user_id: int, page: int, page_size: int):
    """获取浏览历史列表（分页，含新闻详情）。
    实现逻辑和收藏列表类似：
    a) select(func.count()) 查总数
    b) select(History, News).join(News, ...).where(...).order_by(desc(History.view_time))
    c) 拼装数据（id, title, ..., viewTime）
    d) hasMore 计算
    参考 crud/favorite.py 的 get_favorite_list_crud
    """
    # 1. 查总数
    total = await db.execute(select(func.count(History.id)).where(History.user_id == user_id))
    total = total.scalar()

    # 2. 查分页数据
    stmt = select(History, News).join(News, History.news_id == News.id).where(History.user_id == user_id).order_by(desc(History.view_time)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    rows = result.all()
    items = []
    for his,news in rows:
        items.append(HistoryItemBase(
            id=his.id,
            title=news.title,
            description=news.description,
            image=news.image,
            author=news.author,
            publishTime=news.publish_time,
            categoryId=news.category_id,
            views=news.views,
            viewTime=his.view_time,
        ))
    
    # 3. 计算 has_more
    has_more = page_size * page < total

    return HistoryListResponse(items=items, total=total, has_more=has_more)
