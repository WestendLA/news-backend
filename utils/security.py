"""密码加密与校验工具。

用 bcrypt 替代 passlib(bcrypt 5.x 原生 API)。
bcrypt 操作的是 bytes，这里封装成 str 接口方便外部调用。
"""
import bcrypt


def get_hashed_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希，返回字符串。"""
    password_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文 vs 已哈希的密码。"""
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)
