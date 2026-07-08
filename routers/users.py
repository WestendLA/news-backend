from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import authenticate_user, change_password, create_token, create_user, get_user_data, update_user
from schemas.users import PasswordUpdateRequest, UserAuthResponse, UserInfoResponse, UserRequest, UserUpdateRequest
from utils.auth import get_current_user
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


@router.get("/info")
async def get_user_info(
    current_user = Depends(get_current_user),
):
    """获取当前用户信息。"""
    return success_response(data=UserInfoResponse.model_validate(current_user))


# ↓↓↓ 第四步：写 PUT /update 路由（需认证）↓↓↓
#
# @router.put("/update")
# async def update_user_info(
#     update_data: UserUpdateRequest,              # 请求体（自动校验）
#     current_user = Depends(get_current_user),    # 当前登录用户
#     db: AsyncSession = Depends(get_db),          # session
# ):
#     """更新当前用户信息。"""
#     # 1. 调 update_user(db, current_user.id, update_data.model_dump(exclude_none=True))
#     #    exclude_none=True 只保留前端传了值的字段
#     # 2. if not updated_user: raise HTTPException(404, "用户不存在")
#     # 3. 返回 success_response(message="更新成功", data=UserInfoResponse.model_validate(updated_user))
#
# 需要导入：
# - from crud.users import update_user
# - from schemas.users import UserUpdateRequest
#
# 提示：
# - update_data.model_dump(exclude_none=True) 把 Pydantic 模型转 dict，排除 None 字段
# - 路由参数名跟 crud 函数参数名可能不同，用关键字传参 model_dump()

@router.put("/update")
async def update_user_info(
    update_data: UserUpdateRequest,              # 请求体（自动校验）
    current_user = Depends(get_current_user),    # 当前登录用户
    db: AsyncSession = Depends(get_db),          # session
):
    """更新当前用户信息。"""
    # 1. 调 update_user(db, current_user.id, update_data.model_dump(exclude_none=True))
    #    exclude_none=True 只保留前端传了值的字段
    # 2. if not updated_user: raise HTTPException(404, "用户不存在")
    # 3. 返回 success_response(message="更新成功", data=UserInfoResponse.model_validate(updated_user))
    updated_user = await update_user(db, current_user.username, update_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return success_response(message="更新成功", data=UserInfoResponse.model_validate(updated_user))


# ↓↓↓ 写 PUT /password 路由（需认证）↓↓↓
#
# @router.put("/password")
# async def update_password(
#     password_data: PasswordUpdateRequest,          # 请求体（旧密码 + 新密码）
#     current_user = Depends(get_current_user),      # 当前登录用户
#     db: AsyncSession = Depends(get_db),            # session
# ):
#     """修改当前用户密码。"""
#     # 1. 调 update_password(db, current_user.id, password_data.old_password, password_data.new_password)
#     # 2. 拿返回值 (success, message)
#     # 3. if not success: 根据 message 内容返回对应错误
#     #    比如 "旧密码错误" → 400，"用户不存在" → 404
#     # 4. 成功返回 success_response(message="密码修改成功", data=None)
#
# 需要导入：
# - from crud.users import update_password
# - from schemas.users import PasswordUpdateRequest

@router.put("/password")
async def update_password(
    password_data: PasswordUpdateRequest,          # 请求体（旧密码 + 新密码）
    current_user = Depends(get_current_user),      # 当前登录用户
    db: AsyncSession = Depends(get_db),            # session
):
    """修改当前用户密码。"""
    # 调 change_password(db, 用户名, 旧密码, 新密码)
    res_change_pwd = await change_password(
        db, current_user,
        password_data.old_password, password_data.new_password
    )
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码修改失败，请检查旧密码是否正确")
    return success_response(message="密码修改成功")