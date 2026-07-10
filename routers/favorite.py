"""收藏相关 API 路由（需认证）。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.favorite import add_favorite_crud, check_favorite as check_favorite_crud, get_favorite_list_crud, remove_favorite_crud
from schemas.favorite import AddFavoriteRequest, FavoriteCheckResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["收藏"])


# ↓↓↓ 写 GET /check 路由（需认证）↓↓↓
#
# @router.get("/check")
# async def check_favorite(
#     newsId: int = Query(..., description="新闻ID"),
#     current_user = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """检查当前用户是否收藏了某新闻。"""
#     # 1. 调 crud 的 check_favorite(db, current_user.id, newsId)
#     # 2. 返回 {"isFavorite": result}
#     #
#     # 注意：参数名 newsId（驼峰），传给 crud 时可能需转下划线
#     # 返回格式参考 API 文档：{"code":200,"message":"success","data":{"isFavorite": bool}}

@router.get("/check")
async def check_favorite(
    newsId: int = Query(..., description="新闻ID"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """检查当前用户是否收藏了某新闻。"""
    is_favorite = await check_favorite_crud(db, current_user.id, newsId)
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorite))


# ↓↓↓ 写 POST /add 路由（需认证）↓↓↓
#
# @router.post("/add")
# async def add_favorite(
#     add_data: AddFavoriteRequest,             # 请求体 {newsId: 1}
#     current_user = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """添加收藏。"""
#     # 1. 调 add_favorite(db, current_user.id, add_data.newsId)
#     # 2. 返回 success_response(message="收藏成功", data=FavoriteResponse)
#     #
#     # 需要导入：
#     # - from crud.favorite import add_favorite as add_favorite_crud
#     # - from schemas.favorite import AddFavoriteRequest, FavoriteResponse（如有）
#     #
#     # 提示：
#     # - 注意函数名不要和 import 的 crud 函数重名
#     # - 返回值按 API 文档：{id, userId, newsId, createTime}
@router.post("/add")
async def add_favorite(
    add_data: AddFavoriteRequest,             # 请求体 {newsId: 1}
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加收藏。"""
    # 1. 调 add_favorite(db, current_user.id, add_data.newsId)
    # 2. 返回 success_response(message="收藏成功", data=FavoriteResponse)
    #
    # 需要导入：
    # - from crud.favorite import add_favorite as add_favorite_crud
    # - from schemas.favorite import AddFavoriteRequest, FavoriteResponse（如有）
    #
    # 提示：
    # - 注意函数名不要和 import 的 crud 函数重名
    # - 返回值按 API 文档：{id, userId, newsId, createTime}
    result = await add_favorite_crud(db, current_user.id, add_data.news_id)
    if not result:
        return success_response(message="已收藏")
    return success_response(message="收藏成功", data={
        "id": result.id,
        "userId": result.user_id,
        "newsId": result.news_id,
        "createTime": result.created_at,
    })


# ↓↓↓ 写 DELETE /remove 路由（需认证）↓↓↓
#
# @router.delete("/remove")
# async def remove_favorite(
#     newsId: int = Query(..., description="新闻ID"),
#     current_user = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """取消收藏。"""
#     # 1. 调 crud 的 remove_favorite(db, current_user.id, newsId)
#     # 2. if not success: 返回 404 或提示"未收藏"
#     # 3. 返回 success_response(message="取消收藏成功", data=None)
#     #
#     # 需要导入：
#     # - from crud.favorite import remove_favorite
   
@router.delete("/remove")
async def remove_favorite(
    newsId: int = Query(..., description="新闻ID"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消收藏。"""
    # 1. 调 crud 的 remove_favorite(db, current_user.id, newsId)
    # 2. if not success: 返回 404 或提示"未收藏"
    # 3. 返回 success_response(message="取消收藏成功", data=None)
    #
    # 需要导入：
    # - from crud.favorite import remove_favorite
    success = await remove_favorite_crud(db, current_user.id, newsId)
    if not success:
        return success_response(message="未收藏")
    return success_response(message="取消收藏成功", data=None)


# ↓↓↓ 写 GET /list 路由（需认证）↓↓↓
#
# @router.get("/list")
# async def get_favorite_list(
#     page: int = Query(1, description="页码", ge=1),
#     pageSize: int = Query(10, description="每页条数", ge=1, le=100),
#     current_user = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """获取当前用户的收藏列表。"""
#     # 1. 调 crud 的 get_favorite_list(db, current_user.id, page, pageSize)
#     # 2. 返回 success_response(data=result)
#     #
#     # 需要导入：
#     # - from crud.favorite import get_favorite_list

@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, description="页码", ge=1),
    pageSize: int = Query(10, description="每页条数", ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的收藏列表。"""
    # 1. 调 crud 的 get_favorite_list(db, current_user.id, page, pageSize)
    # 2. 返回 success_response(data=result)
    #
    # 需要导入：
    # - from crud.favorite import get_favorite_list_crud
    result = await get_favorite_list_crud(db, current_user.id, page, pageSize)
    return success_response(message="获取收藏列表成功", data=result)