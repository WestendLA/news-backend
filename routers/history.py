"""浏览历史 API 路由（需认证）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.history import add_history
from schemas.history import AddHistoryRequest, HistoryResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["浏览历史"])


@router.post("/add")
async def add_history_view(
    add_data: AddHistoryRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加浏览记录。"""
    history = await add_history(db, current_user.id, add_data.news_id)
    return success_response(message="添加成功", data=HistoryResponse.model_validate(history))


# ↓↓↓ 写 GET /list 路由（需认证）↓↓↓
#
# @router.get("/list")
# async def get_history_list(
#     page: int = Query(1, description="页码", ge=1),
#     pageSize: int = Query(10, description="每页条数", ge=1, le=100),
#     current_user = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """获取浏览历史列表。"""
#     # 1. 调 crud 的 get_history_list(db, current_user.id, page, pageSize)
#     # 2. 返回 success_response(data=result)
#     #
#     # 需要导入：
#     # - from crud.history import get_history_list
#     # - from fastapi import Query
