"""收藏数据访问层（CRUD）。"""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite


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