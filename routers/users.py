from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import create_token, create_user, get_user_data
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest
from utils.response import success_response

router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
  if await get_user_data(db, user_data.username):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
  
  new_user = await create_user(db, user_data)
  token = await create_token(db, new_user.id)

  # return {
  #   "code": 200,
  #   "message": "注册成功",
  #   "data": {
  #   "token": token,
  #   "userInfo": {
  #     "id": new_user.id,
  #     "username": new_user.username,
  #     "bio": new_user.bio,
  #     "avatar": new_user.avatar
  #   }
  # }}  
  user_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(new_user))
  return success_response(message="注册成功", data=user_data)


