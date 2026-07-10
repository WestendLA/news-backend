"""收藏数据模型（SQLAlchemy ORM）。

对应数据库表 favorite：
- id         int unsigned    PRI, auto_increment
- user_id    int unsigned    NOT NULL, MUL（外键 → user.id）
- news_id    int unsigned    NOT NULL, MUL（外键 → news.id）
- created_at timestamp       NOT NULL, 默认 CURRENT_TIMESTAMP  ← 从 Base 继承

提示：
- __tablename__ = "favorite"
- 联合唯一约束可以考虑加（防止重复收藏），但不是必须
- created_at 从 Base 继承，不用写
"""
import datetime

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass



# ↓↓↓ 定义 Favorite 模型 ↓↓↓
#
# class Favorite(Base):
#     __tablename__ = "favorite"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="收藏ID")
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, comment="用户ID")
#     news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, comment="新闻ID")
#
#     
#
# 提示：
# - Mapped[int] 自动推断 Integer，mapped_column 里不用写 Integer
# - ForeignKey 从 sqlalchemy import ForeignKey（已导入）

class Favorite(Base):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(nullable=False, comment="新闻ID")
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, comment="收藏时间")

    __table_args__ = (
        # UniqueConstraint（当前用户、当前新闻）防止重复收藏
        UniqueConstraint("user_id", "news_id", name="idx_favorite_user_news"),
        Index("idx_favorite_user_id", "user_id"),
        Index("idx_favorite_news_id", "news_id"),
    )
    
    def __repr__(self):
        return f"Favorite(user_id={self.user_id}, news_id={self.news_id}, created_at={self.created_at})"
    