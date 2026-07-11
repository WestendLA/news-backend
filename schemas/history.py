"""浏览历史数据校验模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddHistoryRequest(BaseModel):
    """添加浏览记录请求体。"""
    news_id: int = Field(..., alias="newsId", description="新闻ID")

    model_config = {"from_attributes": True, "populate_by_name": True}

class HistoryResponse(BaseModel):
    """浏览历史响应体。"""
    id: int = Field(..., description="浏览记录ID")
    user_id: int = Field(..., description="用户ID")
    news_id: int = Field(..., description="新闻ID")
    view_time: datetime = Field(..., description="浏览时间")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ↓↓↓ 定义 HistoryItemBase（继承 NewsItemBase）和 HistoryListResponse ↓↓↓
#
# class HistoryItemBase(NewsItemBase):
#     """历史记录条目。"""
#     view_time: Optional[datetime] = Field(None, alias="viewTime")
#
#     model_config = {"from_attributes": True, "populate_by_name": True}
#
# class HistoryListResponse(BaseModel):
#     """历史列表响应。"""
#     items: list[HistoryItemBase] = Field(default=[], alias="list")
#     total: int
#     has_more: bool = Field(alias="hasMore")
#
# 提示：
# - 和收藏列表类似，引用 schemas.news 的 NewsItemBase