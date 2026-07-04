"""数据库配置（MySQL + aiomysql 异步驱动 + SQLAlchemy 异步 ORM）。

本文件负责：
1. 定义数据库连接配置（主机、端口、用户名、密码、库名等）
2. 创建异步引擎 create_async_engine
3. 创建会话工厂 async_sessionmaker

关键技术点：
- 异步驱动用 aiomysql，所以连接串前缀是 mysql+aiomysql://
- engine 是“连接池 + 连接工厂”，全局只建一个
- sessionmaker 是“会话工厂”，每次请求用它 new 一个 session 来操作数据库
- 注意：Base 已迁移到 models/news.py，本文件不再定义 Base
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ↓↓↓ 第一步：数据库连接配置 ↓↓↓
# 这些值建议从 .env 读（用 pydantic-settings），现在先硬编码占位，后续再改。
# 示例：
# DB_HOST = "localhost"
# DB_PORT = 3306
# DB_USER = "root"
# DB_PASSWORD = "1234"
# DB_NAME = "news_app"


# ↓↓↓ 第二步：拼接异步连接串 DATABASE_URL ↓↓↓
# 格式：mysql+aiomysql://用户名:密码@主机:端口/库名?charset=utf8mb4
# 提示：用 f-string 把上面的配置拼起来，密码等敏感信息如果有特殊字符需要注意编码。
# DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# ↓↓↓ 第三步：创建异步引擎 engine ↓↓↓
# engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20, pool_recycle=3600)
# 参数说明：
#   echo=True      打印执行的 SQL（学习阶段开着，看清每条 SQL；上线可关）
#   pool_size      连接池常驻连接数
#   max_overflow   超出常驻后还能临时开的连接数
#   pool_recycle   连接回收周期（秒），MySQL 默认 wait_timeout 8 小时，建议设短点避免连接失效


# ↓↓↓ 第四步：创建会话工厂 AsyncSessionLocal ↓↓↓
# AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# 参数说明：
#   expire_on_commit=False  commit 之后对象不过期，否则异步里再访问属性会触发隐式 IO 报错


# 注意：Base 已迁移到 models/news.py，需要时 from models.news import Base

# ↓↓↓ 第五步：定义依赖 get_db，给路由提供 session ↓↓↓
#
# 提示（你来写）：
#
# async def get_db():
#     async with AsyncSessionLocal() as session:   # 用会话工厂 new 一个 session
#         yield session                            # 把 session 交给路由用
#     # 离开 with 块时 session 自动关闭
#
# 说明：
# - 这是一个“生成器依赖”：用 yield 而不是 return
# - FastAPI 看到 yield，会把 yield 出去的 session 注入到路由的 db 参数
# - 路由函数执行完后，才回来执行 yield 之后的清理（这里 with 块自动 close）
# - 为什么不每个路由手动 new + close？封装成依赖后，17 个接口都能复用，不重复、不漏关
#
# 类型注解：yield 出去的是 AsyncSession，路由那边 db: AsyncSession = Depends(get_db)

# TODO: 后续可用 pydantic-settings 的 BaseSettings 从 .env 统一读取配置。

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "1234"
DB_NAME = "news_app"

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20, pool_recycle=3600)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session