"""AI掘金头条新闻系统 - 应用入口。

学习练习版：基础结构已搭好，根路由由你来写。
目标：定义一个 GET / 路由，返回 {"message": "hello world"}
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import favorite, history, news, users
from utils.exception_handler import register_exception_handlers

app = FastAPI(
    title="AI掘金头条新闻系统",
    description="仿今日头条的新闻系统后端 API 服务",
    version="0.1.0",
)

register_exception_handlers(app)

# 配置 CORS 中间件
# 开发环境放通所有来源；生产环境应收紧 allow_origins 为具体的前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ↓↓↓ 在这里写你的根路由 ↓↓↓
# 提示：
# 1. 用装饰器声明路由：@app.get("/")   （GET 请求，路径为根 /）
# 2. 定义一个函数：async def root():
# 3. 在函数里 return 一个字典：{"message": "hello world"}
# 4. FastAPI 会自动把返回的 dict 转成 JSON
@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}!"}

# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
