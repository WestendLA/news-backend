# AI掘金头条新闻系统（toutiao_backend）

一个基于 **FastAPI + SQLAlchemy（异步）** 构建的仿今日头条新闻系统**后端 API 服务**。

提供用户注册登录、新闻浏览（分类 / 列表 / 详情）、收藏、浏览历史等功能，供前端（App / 网页）调用。

> ⚠️ 本项目为**学习练习版**：代码中保留了大量中文教学注释与"你来写"的模板引导，属正常现象。

---

## 目录

- [技术栈](#技术栈)
- [功能特性](#功能特性)
- [目录结构](#目录结构)
- [快速开始](#快速开始)
- [数据库设计](#数据库设计)
- [API 概览](#api-概览)
- [认证机制](#认证机制)
- [统一响应与错误处理](#统一响应与错误处理)
- [Redis 缓存](#redis-缓存)
- [测试](#测试)
- [已知问题与注意事项](#已知问题与注意事项)
- [新手学习路线](#新手学习路线)

---

## 技术栈

| 技术 | 版本 | 用途 |
|---|---|---|
| Python | 3.11 | 编程语言 |
| FastAPI | 0.138 | Web 框架：路由、参数校验、自动生成接口文档 |
| Uvicorn | 0.49 | ASGI 服务器，负责启动服务 |
| Pydantic | 2.13 | 请求/响应数据校验（`schemas/` 目录） |
| SQLAlchemy | 2.0（异步） | ORM，用 Python 类操作数据库 |
| aiomysql | 0.3 | MySQL 异步驱动 |
| MySQL | — | 主数据库 |
| Redis | — | 缓存热点数据（分类、新闻列表） |
| bcrypt | 5.0 | 密码加密与校验（原生 API，非 passlib） |
| pytest | — | 自动化测试 |

技术特点：**全异步（async/await）**，IO 操作不阻塞，单进程即可支撑较高并发。

---

## 功能特性

### 用户模块
- 用户注册、登录
- 获取 / 更新用户信息
- 修改密码

### 新闻模块
- 获取新闻分类
- 获取新闻列表（分页 + 分类筛选）
- 获取新闻详情（浏览量 +1，附带相关新闻推荐）

### 收藏模块
- 添加 / 取消收藏
- 检查收藏状态
- 收藏列表（分页）
- 清空收藏

### 浏览历史模块
- 添加浏览记录（重复浏览自动更新时间）
- 浏览历史列表（分页）
- 删除单条 / 清空历史

---

## 目录结构

采用经典**分层架构**，请求从外到内：`routers → crud → models → MySQL`，`schemas` 负责数据校验，`cache/` 负责 Redis 缓存。

```
toutiao_backend/
├── main.py                    # 应用入口：创建 app、注册中间件/异常处理、挂载路由
├── requirements.txt           # 依赖清单
├── .env.example               # 环境变量示例（当前配置仍为硬编码，见"已知问题"）
├── config/                    # 配置层
│   ├── db_conf.py             #   MySQL 连接、异步引擎、会话工厂、get_db 依赖
│   └── cache_config.py        #   Redis 连接配置
├── models/                    # ORM 模型层（Python 类 ↔ 数据库表）
│   ├── news.py                #   Base、Category(news_category)、News(news)
│   ├── users.py               #   User(user)、UserToken(user_token)
│   ├── favorite.py            #   Favorite(favorite)
│   └── history.py             #   History(history)
├── schemas/                   # Pydantic 校验模型（请求体 / 响应体）
│   ├── news.py                #   NewsItemBase
│   ├── users.py               #   UserRequest、UserAuthResponse 等
│   ├── favorite.py            #   AddFavoriteRequest、FavoriteListResponse 等
│   └── history.py             #   AddHistoryRequest、HistoryListResponse 等
├── crud/                      # 数据访问层（数据库读写逻辑）
│   ├── news.py                #   分类 / 列表(带缓存) / 详情 / 浏览量+1 / 相关新闻
│   ├── users.py               #   注册 / 登录 / token / 更新资料 / 改密码
│   ├── favorite.py            #   收藏增删查清
│   └── history.py             #   历史增删查清
├── routers/                   # 路由层（URL、参数校验、调用 crud、拼响应）
│   ├── news.py                #   /api/news/*
│   ├── users.py               #   /api/user/*
│   ├── favorite.py            #   /api/favorite/*（需认证）
│   └── history.py             #   /api/history/*（需认证）
├── utils/                     # 通用工具
│   ├── auth.py                #   认证依赖 get_current_user（解析 token）
│   ├── security.py            #   bcrypt 密码加密 / 校验
│   ├── response.py            #   统一成功响应 {code, message, data}
│   ├── exception.py           #   各类异常处理逻辑
│   └── exception_handler.py   #   注册全局异常处理器
├── cache/
│   └── news_cache.py          # Redis 缓存键封装（news:categories、news:list:*）
├── tests/                     # pytest 测试
│   └── test_utils/
│       ├── test_security.py   #   密码加密 / 校验
│       └── test_response.py   #   统一响应格式
├── API接口规范文档.md          # 接口详细规范（请求/响应示例）
└── 项目后端设计说明文档.md      # 设计说明
```

### 一次请求的完整链路（以 `GET /api/news/list` 为例）

```
GET /api/news/list?categoryId=1&page=1&pageSize=10
    │
    ▼
routers/news.py  get_news_list()          # ① 校验参数（categoryId 必填、pageSize ≤ 100）
    ▼
crud/news.py  get_news_list_cached()      # ② 先查 Redis 缓存 news:list:1:1:10
                                          # ③ 未命中 → SQLAlchemy 查 MySQL（列表 + 总数）→ 回填缓存
    ▼
返回 {"code":200, "message":"success", "data":{"list":[...], "total":100, "hasMore":true}}
```

---

## 快速开始

### 环境要求

- Python 3.11+（仓库内自带 `.venv` 虚拟环境）
- MySQL（库名 `news_app`，需建好 6 张表，见 [数据库设计](#数据库设计)）
- Redis（默认 `localhost:6379`）

### 1. 安装依赖

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. 配置数据库与 Redis

连接配置通过 **pydantic-settings** 读取（优先级：环境变量 > `.env` 文件 > 代码默认值），字段定义在 `config/settings.py`：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `DB_HOST` / `DB_PORT` | `localhost` / `3306` | MySQL 地址 |
| `DB_USER` / `DB_PASSWORD` | `root` / 空 | MySQL 账号 |
| `DB_NAME` | `news_app` | 数据库名 |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` | `localhost` / `6379` / `0` | Redis 地址 |

本地开发按需创建 `.env`（复制模板后修改），**不建 `.env` 也能用默认值启动**：

```powershell
Copy-Item .env.example .env
# 然后编辑 .env，填入你的 DB_PASSWORD 等
```

> ⚠️ `.env` 已被 `.gitignore` 忽略，不会提交到仓库；请勿把真实密码写进 `.env.example`。
>
> 没有建表脚本 / migration（未引入 Alembic），需要手动建表，表结构见 [数据库设计](#数据库设计)。

### 3. 启动服务

```powershell
# 方式一
.venv\Scripts\python.exe main.py

# 方式二
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

服务默认运行在 `http://127.0.0.1:8000`。

### 4. 查看接口文档

FastAPI 自动生成，**强烈推荐新人从这里上手**：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

### 5. 快速体验

```powershell
# 注册
curl -X POST http://127.0.0.1:8000/api/user/register -H "Content-Type: application/json" -d '{"username":"demo","password":"123456"}'

# 登录（返回 token）
curl -X POST http://127.0.0.1:8000/api/user/login -H "Content-Type: application/json" -d '{"username":"demo","password":"123456"}'

# 新闻列表（无需登录）
curl "http://127.0.0.1:8000/api/news/list?categoryId=1&page=1&pageSize=10"

# 收藏（需带 token）
curl -X POST http://127.0.0.1:8000/api/favorite/add -H "Authorization: <token>" -H "Content-Type: application/json" -d '{"newsId":1}'
```

---

## 数据库设计

共 6 张表（模型定义在 `models/`，已对照真实表结构编写）：

| 表 | 用途 | 关键字段 |
|---|---|---|
| `user` | 用户 | `username`(唯一)、`password`(bcrypt 密文)、`nickname`、`avatar`、`gender`、`bio`、`phone` |
| `user_token` | 登录令牌 | `user_id`(外键)、`token`(唯一)、`expires_at`(7 天过期) |
| `news_category` | 新闻分类 | `name`(唯一)、`sort_order` |
| `news` | 新闻 | `title`、`description`、`content`、`image`、`author`、`category_id`(外键)、`views`、`publish_time`；索引：`category_id`、`publish_time` |
| `favorite` | 收藏 | `user_id` + `news_id`（联合唯一约束，防重复收藏） |
| `history` | 浏览历史 | `user_id`、`news_id`、`view_time` |

> 注意：`models/news.py` 定义了带 `created_at` / `updated_at` 时间戳的 `Base`；`models/users.py`、`models/favorite.py`、`models/history.py` 各自定义了独立的 `Base`（无时间戳继承），多个 Base 并非同一个类。

---

## API 概览

基础路径：`http://localhost:8000`，完整请求/响应示例见 `API接口规范文档.md`。

### 用户 `/api/user`（注册登录不需要认证，其余需要）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/user/register` | 注册（返回 token + userInfo） |
| POST | `/api/user/login` | 登录（返回 token + userInfo） |
| GET | `/api/user/info` | 获取当前用户信息 |
| PUT | `/api/user/update` | 更新用户信息 |
| PUT | `/api/user/password` | 修改密码 |

### 新闻 `/api/news`（无需认证）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/news/categories` | 获取分类列表（支持 skip / limit） |
| GET | `/api/news/list` | 新闻列表，参数 `categoryId`(必填)、`page`、`pageSize`(≤100) |
| GET | `/api/news/detail` | 新闻详情，参数 `id`；浏览量 +1，返回 `relatedNews` |

### 收藏 `/api/favorite`（需认证）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/favorite/check` | 检查是否已收藏，参数 `newsId` |
| POST | `/api/favorite/add` | 添加收藏，body `{newsId}` |
| DELETE | `/api/favorite/remove` | 取消收藏，参数 `newsId` |
| GET | `/api/favorite/list` | 收藏列表，参数 `page`、`pageSize` |
| DELETE | `/api/favorite/clear` | 清空收藏 |

### 浏览历史 `/api/history`（需认证）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/history/add` | 添加浏览记录，body `{newsId}` |
| GET | `/api/history/list` | 历史列表，参数 `page`、`pageSize` |
| DELETE | `/api/history/delete/{history_id}` | 删除单条记录 |
| DELETE | `/api/history/clear` | 清空历史 |

---

## 认证机制

- 注册 / 登录成功后生成随机 `uuid4` token，存入 `user_token` 表，**有效期 7 天**，返回给前端
- 后续请求在请求头携带：`Authorization: <token>`（兼容 `Authorization: Bearer <token>`）
- 需要认证的接口通过 `Depends(get_current_user)`（`utils/auth.py`）校验 token 有效性及过期时间
- **token 无效或过期 → 401**

---

## 统一响应与错误处理

成功响应统一格式（由 `utils/response.py` 的 `success_response` 生成）：

```json
{ "code": 200, "message": "success", "data": {} }
```

全局异常处理（`utils/exception_handler.py` 注册，顺序为"具体在前、兜底在后"）：

| 异常类型 | 场景 | HTTP 状态码 |
|---|---|---|
| `HTTPException` | 业务错误（如"用户名已存在"、认证失败） | 400 / 401 / 404 等 |
| `IntegrityError` | 数据库约束冲突（用户名重复、外键不存在） | 400 |
| `SQLAlchemyError` | 数据库操作失败 | 500 |
| `Exception` | 兜底（未捕获异常） | 500 |

> 开发模式（`utils/exception.py` 中 `DEBUG_MODE = True`）下，数据库/未知异常会附带详细错误信息（error_type、traceback、path），方便排查；上线前应关闭。

---

## Redis 缓存

采用 **Cache-Aside（旁路缓存）** 策略：先查缓存，未命中再查库并回填。

| 缓存键 | 内容 | 过期时间 |
|---|---|---|
| `news:categories` | 新闻分类列表 | 2 小时 |
| `news:list:{categoryId\|all}:{page}:{size}` | 新闻列表分页结果 | 2 小时 |

缓存封装在 `cache/news_cache.py`，底层工具在 `utils/cache.py`（Redis 不可用时自动降级为直接查库，不影响业务）。

---

## 测试

```powershell
.venv\Scripts\python.exe -m pytest tests -q
```

当前覆盖（均为**纯函数单元测试**，不依赖数据库 / 网络）：

- `tests/test_utils/test_security.py` —— bcrypt 加密与校验
- `tests/test_utils/test_response.py` —— 统一响应格式

接口级（集成）测试尚未补充，欢迎贡献。

---

## 已知问题与注意事项

1. **没有建表脚本 / migration**：未引入 Alembic，换环境需手动建表（表结构见 [数据库设计](#数据库设计)）。
2. **多个 Base 类**：`models/` 下存在多个独立的 `DeclarativeBase`，并非同一个，混用需注意。
3. **小瑕疵**：`routers/history.py` 删除单条记录失败时返回文案为"未收藏"；`routers/favorite.py` 收藏列表返回字段使用 `list`（响应模型 alias）。
4. **CORS 放通所有来源**（`main.py`）：开发环境方便调试，生产环境应收紧 `allow_origins`。
5. 设计文档中提及的"新闻详情缓存 / 历史记录缓存"尚未实现，以代码实际为准。

---

## 新手学习路线

1. 启动服务，打开 `http://127.0.0.1:8000/docs`，把所有接口点一遍，建立整体认知
2. 按顺序精读：`main.py`（入口）→ `routers/news.py`（最简单路由）→ `crud/news.py`（查询逻辑）→ `models/news.py`（ORM 映射）→ `schemas/`（Pydantic 校验）
3. 跟随 [一次请求的完整链路](#一次请求的完整链路以-get-apinewslist-为例) 走一遍 `GET /api/news/list`
4. 运行 pytest 现有测试，再尝试模仿着为某个接口补充测试
5. 参照 `API接口规范文档.md` 用 Swagger UI 或 curl 验证接口行为

---

## License

教学练习项目，无特定许可证。
