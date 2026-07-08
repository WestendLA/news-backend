from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class UserRequest(BaseModel):
    username: str
    password: str

class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


# ↓↓↓ 第四步：定义 UserUpdateRequest，更新用户信息时用 ↓↓↓
#
# class UserUpdateRequest(BaseModel):
#     """更新用户信息请求体（全部可选）。"""
#     nickname: Optional[str] = Field(None, max_length=50, description="昵称")
#     avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
#     gender: Optional[str] = Field(None, max_length=10, description="性别")
#     bio: Optional[str] = Field(None, max_length=500, description="个人简介")
#     phone: Optional[str] = Field(None, max_length=20, description="手机号")
#
# 提示：
# - 所有字段都是 Optional + default=None，调用者只传要更新的字段
# - UserInfoBase 已有 nickname/avatar/gender/bio，可以继承它再补 phone
# - 或者直接重写一份，更清晰（选哪种都行）

class UserUpdateRequest(UserInfoBase):
    """更新用户信息请求体（全部可选）。"""
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    gender: Optional[str] = Field(None, description="性别")
    bio: Optional[str] = Field(None, description="个人简介")
    phone: Optional[str] = Field(None, description="手机号")


# ↓↓↓ 定义 PasswordUpdateRequest ↓↓↓
#
# class PasswordUpdateRequest(BaseModel):
#     """修改密码请求体。"""
#     old_password: str = Field(..., description="当前密码")
#     new_password: str = Field(..., description="新密码")
#
# 提示：
# - 两个字段都是必填（Field(..., ...) 表示必填）
# - 字段名可用 oldPassword / newPassword 对齐前端，自己决定

class PasswordUpdateRequest(BaseModel):
    """修改密码请求体。"""
    old_password: str = Field(..., alias="oldPassword", description="当前密码")
    new_password: str = Field(..., alias="newPassword", description="新密码")

# data 数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 对象属性中取值
    )
