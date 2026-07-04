from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from models.users import User, UserToken
from typing import Optional

from schemas.users import UserRequest
from utils.security import get_hashed_password
import uuid



async def get_user_data(db: AsyncSession, username: str):
    """
    获取用户数据
    """
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserRequest):
    """
    创建用户
    """
    hashed_password = get_hashed_password(user.password)
    new_user = User(username=user.username, password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def create_token(db: AsyncSession, user_id: int):
    """
    创建 token
    """
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
        await db.commit()
    else:
        db.add(UserToken(user_id=user_id, token=token, expires_at=expires_at))
        await db.commit()
    return token