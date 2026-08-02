"""Redis 连接配置（从 config.settings 读取，支持 .env 覆盖）。"""
from config.settings import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB
REDIS_PASSWORD = settings.REDIS_PASSWORD
