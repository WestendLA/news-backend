from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, func, update
from models.news import Category, News



async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = None):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# ↓↓↓ 第二步：写 get_news_list 查询函数 ↓↓↓
#
# def get_news_list(db: AsyncSession, category_id: int, page: int = 1, page_size: int = 10):
#     """获取新闻列表（分页 + 分类筛选）。
#
#     参数：
#       db          - 会话
#       category_id - 分类ID（必填）
#       page        - 页码，从 1 开始
#       page_size   - 每页条数，默认 10，最大 100
#
#     返回：
#       {"list": [...], "total": int, "hasMore": bool}
#     """
#     需要：
#     1. from models.news import News
#     2. from sqlalchemy import func, desc
#
#     实现步骤：
#     a) 查总数（用于分页和 hasMore）
#        count_stmt = select(func.count()).select_from(News).where(News.category_id == category_id)
#        total = (await db.execute(count_stmt)).scalar()
#
#     b) 查当前页的数据
#        offset = (page - 1) * page_size
#        stmt = (
#            select(News)
#            .where(News.category_id == category_id)
#            .order_by(desc(News.publish_time))
#            .offset(offset)
#            .limit(page_size)
#        )
#        result = await db.execute(stmt)
#        news_list = result.scalars().all()
#
#     c) 算 hasMore
#        has_more = offset + page_size < total
#
#     d) 返回 dict（list 里 ORM 对象转字典，和 get_categories 返回方式一致）
#        return {"list": [...], "total": total, "hasMore": has_more}
#
# 提示：
# - func.count() 在文件顶部已经 from sqlalchemy import func 了
# - desc() 需要 from sqlalchemy import desc
# - category_id 是必填参数（不给默认值），page 和 page_size 有默认值

async def list_news(db: AsyncSession, category_id: int, page: int = 1, page_size: int = 10):
    """获取新闻列表（分页 + 分类筛选）。
    参数：
      db          - 会话
      category_id - 分类ID（必填）
      page        - 页码，从 1 开始
      page_size   - 每页条数，默认 10，最大 100
    """
    stmt = select(News).where(News.category_id == category_id).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    return news_list

async def news_count(db: AsyncSession, category_id: int):
    """获取新闻总数。
    参数：
      db          - 会话
      category_id - 分类ID（必填）
    """
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    total = (await db.execute(stmt)).scalar_one()
    return total

async def news_detail(db: AsyncSession, id: int):
    """获取新闻详情。
    参数：
      db          - 会话
      id          - 新闻ID（必填）
    """
    stmt = select(News).where(News.id == id)
    news = (await db.execute(stmt)).scalar_one_or_none()
    return news

async def increase_views(db: AsyncSession, id: int):
    """增加新闻浏览量。
    参数：
      db          - 会话
      news        - 新闻对象（必填）
    """
    update_stmt = update(News).where(News.id == id).values(views=func.coalesce(News.views, 0) + 1)
    result = await db.execute(update_stmt)
    await db.commit()
    # 检查是否增加成功，成功返回 True，失败返回 False
    return result.rowcount > 0

async def get_related_news(db: AsyncSession, id: int, category_id: int, limit: int = 5):
    """获取相关新闻（分页）。
    参数：
      db          - 会话
      id          - 新闻ID（必填）
      category_id - 分类ID（必填）
      limit       - 每页条数，默认 5，最大 100
    """
    stmt = select(News).where(News.category_id == category_id, News.id != id).order_by(desc(News.views)).limit(limit)
    result = await db.execute(stmt)
    related_news_list = result.scalars().all()
    return related_news_list
  
