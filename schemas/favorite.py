"""收藏数据校验模型（Pydantic）。"""
from pydantic import BaseModel, ConfigDict, Field


# ↓↓↓ 定义 FavoriteCheckResponse ↓↓↓
#
# class FavoriteCheckResponse(BaseModel):
#     """检查收藏状态响应。"""
#     is_favorite: bool
#
# 提示：
# - 字段名用 is_favorite 还是 isFavorite 取决于你前端期望的格式
# - 可以用 alias 做转换（参考 UserAuthResponse 的 alias="userInfo"）
# - model_config = ConfigDict(from_attributes=True) 是否要加？

class FavoriteCheckResponse(BaseModel):
    """检查收藏状态响应。"""
    is_favorite: bool = Field(description="是否收藏",alias="isFavorite")
    
    model_config = ConfigDict(from_attributes=True)


# ↓↓↓ 定义 AddFavoriteRequest（添加收藏请求体）↓↓↓
#
# class AddFavoriteRequest(BaseModel):
#     """添加收藏请求体。"""
#     news_id: int = Field(..., alias="newsId", description="新闻ID")
#
# 提示：
# - 只有一个字段 newsId，但也可以用 Query 参数的方式传，看路由怎么设计

class AddFavoriteRequest(BaseModel):
    """添加收藏请求体。"""
    news_id: int = Field(..., alias="newsId", description="新闻ID")
    
    model_config = ConfigDict(from_attributes=True)