"""新闻模块路由。

把 news 相关接口从 main.py 里拆出来，集中放到这个文件。
main.py 通过 app.include_router(news.router) 把它挂载到应用上，
统一加前缀 /api/news，所以本文件里写路径时不用再带 /api/news。

本文件要实现的接口（路径都是相对于前缀 /api/news 的）：
- GET /categories  获取新闻分类列表
- GET /list        获取新闻列表（支持分页和分类筛选）
- GET /detail      获取新闻详情

学习要点：
1. APIRouter 是“小号 app”，用法和 app 几乎一样：router.get(...)、router.post(...)
2. 这个文件里不创建 FastAPI 应用，只创建一个 router，最后由 main.py 来挂载
3. 路径写相对路径即可，前缀交给 include_router 时的 prefix 参数统一加
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.news import get_categories, get_related_news, increase_views, list_news, news_count, news_detail
from fastapi import HTTPException



# 创建一个路由器实例
# tags=["新闻"] 用于在 /docs 文档里把这一组接口归到"新闻"分组下
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def list_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await get_categories(db=db, skip=skip, limit=limit)
    data = [
        {"id": c.id, "name": c.name, "sort_order": c.sort_order}
        for c in categories
    ]
    return {"code": 200, "msg": "获取新闻分类成功", "data": data}


# ↓↓↓ 第三步：写 GET /list 路由 ↓↓↓
#
# @router.get("/list")
# async def get_news_list(
#     categoryId: int,                     # 必填，问：FastAPI 怎么把 categoryId 映射成 category_id？
#     page: int = 1,                       # 页码，默认 1
#     pageSize: int = 10,                  # 每页条数，默认 10
#     db: AsyncSession = Depends(get_db),  # 依赖注入拿 session
# ):
#     """获取新闻列表。"""
#     # 1. 校验 pageSize 最大为 100（if pageSize > 100: pageSize = 100 或者直接报错）
#
#     # 2. 调 crud 的 get_news_list 拿数据
#     #    注意 crud 函数的参数名和这里的变量名可能不一致
#     #    问：你准备怎么处理 categoryId（驼峰）→ category_id（下划线）的转换？
#
#     # 3. 按 API 规范返回
#     #    return {"code": 200, "message": "success", "data": result}
#
# 需要导入：
# - from crud.news import get_news_list
#
# 提示：
# - API 规范要求参数名是 categoryId（驼峰），但 crud 里用的可能是 category_id（下划线）
# - FastAPI 路由参数直接映射 Query 参数名，注意大小写（categoryId 在路由层保持驼峰）
# - 传给 crud 时可以 keyword argument 做转换
# - 接口文档的返回字段是 "message" 不是 "msg"，注意统一


@router.get("/list")
async def get_news_list(
    categoryId: int = Query(..., description="分类ID"),                     # 必填，问：FastAPI 怎么把 categoryId 映射成 category_id？
    page: int = Query(1, description="页码，默认 1"),                       # 页码，默认 1
    pageSize: int = Query(10, description="每页条数，默认 10", le=100),                  # 每页条数，默认 10
    db: AsyncSession = Depends(get_db),  # 依赖注入拿 session
):
    """获取新闻列表。"""
    news_list = await list_news(db=db, category_id=categoryId, page=page, page_size=pageSize)
    total = await news_count(db=db, category_id=categoryId)
    has_more = (page - 1) * pageSize + pageSize < total
    return {
  "code": 200,
  "message": "success",
  "data": {
    "list": news_list,
    "total": total,
    "hasMore": has_more
  }
}

@router.get("/detail")
async def get_news_detail(
    id: int = Query(..., description="新闻ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取新闻详情。"""
    news = await news_detail(db=db, id=id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    success = await increase_views(db=db, id=id)
    if not success:
        raise HTTPException(status_code=500, detail="更新新闻浏览量失败")

    await db.refresh(news)

    related_news_list = await get_related_news(db=db, id=id, category_id=news.category_id)

    return {
  "code": 200,
  "message": "success",
  "data": {
    "id": news.id,
    "title": news.title,
    "content": news.content,
    "image": news.image,
    "author": news.author,
    "publishTime": news.publish_time,
    "categoryId": news.category_id,
    "views": news.views,
    "relatedNews": [{
      "id": related_news_detail.id,
    "title": related_news_detail.title,
    "content": related_news_detail.content,
    "image": related_news_detail.image,
    "author": related_news_detail.author,
    "publishTime": related_news_detail.publish_time,
    "categoryId": related_news_detail.category_id,
    "views": related_news_detail.views,
    } for related_news_detail in related_news_list]
  }
}
