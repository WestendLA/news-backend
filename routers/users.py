from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import authenticate_user, create_token, create_user, get_user_data
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


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
  # 登录逻辑： 1. 校验用户名是否存在 2. 校验密码是否正确 3. 生成 token
  user = await authenticate_user(db, user_data.username, user_data.password)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
  token = await create_token(db, user.id)
  return success_response(message="登录成功", data=UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user)))
