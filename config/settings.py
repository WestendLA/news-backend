"""应用全局配置（pydantic-settings）。

读取优先级：环境变量 > .env 文件 > 代码默认值。
本地开发：复制 .env.example 为 .env 后按需修改即可生效；
不建 .env 时使用默认值（localhost/root/空密码）也能正常启动。
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """字段名与 .env.example 中的变量名一一对应。"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # 数据库（MySQL）
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "news_app"
    DB_CHARSET: str = "utf8mb4"

    # Redis 缓存
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""


settings = Settings()
