"""数据库配置（MySQL + aiomysql 异步驱动 + SQLAlchemy 异步 ORM）。

本文件负责：
1. 读取数据库连接配置（主机、端口、用户名、密码、库名等）——来自 config.settings（pydantic-settings + .env）
2. 创建异步引擎 create_async_engine
3. 创建会话工厂 async_sessionmaker
4. 定义依赖 get_db，给路由提供 session

关键技术点：
- 异步驱动用 aiomysql，所以连接串前缀是 mysql+aiomysql://
- engine 是“连接池 + 连接工厂”，全局只建一个
- sessionmaker 是“会话工厂”，每次请求用它 new 一个 session 来操作数据库
- 注意：Base 已迁移到 models/news.py，本文件不再定义 Base
"""
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import settings

# 拼接异步连接串 DATABASE_URL
# 格式：mysql+aiomysql://用户名:密码@主机:端口/库名?charset=utf8mb4
# 用户名/密码做 quote_plus 编码，避免密码含 @ : / % 等特殊字符时 URL 解析错误
DATABASE_URL = (
    f"mysql+aiomysql://{quote_plus(settings.DB_USER)}:{quote_plus(settings.DB_PASSWORD)}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset={settings.DB_CHARSET}"
)

# 创建异步引擎 engine
# 参数说明：
#   echo=True      打印执行的 SQL（学习阶段开着，看清每条 SQL；上线可关）
#   pool_size      连接池常驻连接数
#   max_overflow   超出常驻后还能临时开的连接数
#   pool_recycle   连接回收周期（秒），MySQL 默认 wait_timeout 8 小时，建议设短点避免连接失效
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20, pool_recycle=3600)

# 创建会话工厂 AsyncSessionLocal
# expire_on_commit=False：commit 之后对象不过期，否则异步里再访问属性会触发隐式 IO 报错
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    """生成器依赖：把 session 交给路由用，离开 with 块时 session 自动关闭。"""
    async with AsyncSessionLocal() as session:
        yield session
