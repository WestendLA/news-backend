"""收藏数据访问层（CRUD）。"""
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


# ↓↓↓ 写 check_favorite 函数 ↓↓↓
#
# async def check_favorite(db: AsyncSession, user_id: int, news_id: int):
#     """检查某用户是否收藏了某新闻。
#
#     参数：
#       db      - 会话
#       user_id - 用户ID
#       news_id - 新闻ID
#
#     返回：
#       True / False
#
#     实现：
#     stmt = select(Favorite).where(
#         Favorite.user_id == user_id,
#         Favorite.news_id == news_id
#     )
#     result = await db.execute(stmt)
#     fav = result.scalar_one_or_none()
#     return fav is not None
#     """

async def check_favorite(db: AsyncSession, user_id: int, news_id: int):
    """检查某用户是否收藏了某新闻。

    参数：
      db      - 会话
      user_id - 用户ID
      news_id - 新闻ID
    """
    stmt = select(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    fav = result.scalar_one_or_none()
    return fav is not None


# ↓↓↓ 写 add_favorite 函数 ↓↓↓
#
# async def add_favorite(db: AsyncSession, user_id: int, news_id: int):
#     """添加收藏。
#
#     参数：
#       db      - 会话
#       user_id - 用户ID
#       news_id - 新闻ID
#
#     步骤：
#     1. 先查是否已收藏（用 check_favorite）
#     2. 已收藏则直接返回（或返回错误）
#     3. 未收藏则创建 Favorite 对象 → db.add → db.commit → db.refresh
#     4. 返回创建的 Favorite 对象
#
#     提示：
#     - 可以复用上面定义的 check_favorite 来查重复
#     - refresh 后返回对象才有 id 等字段

async def add_favorite_crud(db: AsyncSession, user_id: int, news_id: int):
    """添加收藏。

    参数：
      db      - 会话
      user_id - 用户ID
      news_id - 新闻ID
    """
    if await check_favorite(db, user_id, news_id):
        return None
    fav = Favorite(
        user_id=user_id,
        news_id=news_id
    )
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


# ↓↓↓ 写 remove_favorite 函数 ↓↓↓
#
# async def remove_favorite(db: AsyncSession, user_id: int, news_id: int):
#     """取消收藏。
#
#     参数：
#       db      - 会话
#       user_id - 用户ID
#       news_id - 新闻ID
#
#     返回：
#       True（成功删除）/ False（收藏记录不存在）
#
#     实现提示：
#     - 用 await check_favorite(db, user_id, news_id) 先查是否存在
#     - 不存在 → return False
#     - 存在 → select(Favorite).where(...) → scalar_one_or_none()
#            → await db.delete(fav) → await db.commit() → return True
#     """
#
# 或者直接用 delete() 语句（from sqlalchemy import delete）：
#     stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
#     result = await db.execute(stmt)
#     await db.commit()
#     return result.rowcount > 0
#
# 两种方式都可以，选你喜欢的

async def remove_favorite_crud(db: AsyncSession, user_id: int, news_id: int):
    """取消收藏。"""
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# ↓↓↓ 写 get_favorite_list 函数 ↓↓↓
#
# async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
#     """获取用户收藏列表（分页，含新闻详情）。
#
#     参数：
#       db        - 会话
#       user_id   - 用户ID
#       page      - 页码，从 1 开始
#       page_size - 每页条数，默认 10，最大 100
#
#     返回：
#       {"list": [...], "total": int, "hasMore": bool}
#
#     实现步骤：
#     a) 查总数
#        count_stmt = select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
#        total = (await db.execute(count_stmt)).scalar()
#
#     b) 查当前页 + 连表查新闻信息
#        需要 import News（from models.news import News）
#        stmt = (
#            select(Favorite, News)         # ← 多表查询，返回元组 (Favorite, News)
#            .join(News, Favorite.news_id == News.id)
#            .where(Favorite.user_id == user_id)
#            .order_by(desc(Favorite.created_at))
#            .offset((page - 1) * page_size)
#            .limit(page_size)
#        )
#        result = await db.execute(stmt)
#        rows = result.all()  # 每行 = (Favorite, News)
#
#     c) 拼数据
#        list = []
#        for fav, news in rows:
#            list.append({
#                "id": news.id,
#                "title": news.title,
#                "description": news.description,
#                "image": news.image,
#                "author": news.author,
#                "publishTime": news.publish_time,
#                "categoryId": news.category_id,
#                "views": news.views,
#                "favoriteTime": fav.created_at,
#            })
#
#     d) 算 hasMore
#        has_more = offset + page_size < total
#
#     需要导入：
#     - from sqlalchemy import desc, func
#     - from models.news import News

async def get_favorite_list_crud(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    """获取用户收藏列表（分页，含新闻详情）。"""
    from schemas.favorite import FavoriteItemBase, FavoriteListResponse

    count_stmt = select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
    total = (await db.execute(count_stmt)).scalar()
    stmt = (
        select(Favorite, News)
        .join(News, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(desc(Favorite.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for fav, news in rows:
        items.append(FavoriteItemBase(
            id=news.id,
            title=news.title,
            description=news.description,
            image=news.image,
            author=news.author,
            categoryId=news.category_id,
            views=news.views,
            publishTime=news.publish_time,
            favoriteId=fav.id,
            favoriteTime=fav.created_at,
        ))

    has_more = (page - 1) * page_size + page_size < total
    return FavoriteListResponse(items=items, total=total, hasMore=has_more)