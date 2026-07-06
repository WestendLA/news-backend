"""认证依赖：提供 get_current_user，供需要登录的接口使用。"""
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import get_user_by_token

# 从 Authorization 头提取原始值，不强制要求 "Bearer " 前缀
security_scheme = APIKeyHeader(name="Authorization")


async def get_current_user(
    auth_header: str = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """兼容 "Bearer <token>" 和 "<token>" 两种格式。"""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]  # 去掉 "Bearer " 前缀
    else:
        token = auth_header      # 直接当 token 用

    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 token")
    return user
