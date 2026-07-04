"""新闻数据模型（SQLAlchemy ORM，2.x 新写法 mapped_column）。

本文件定义：
1. Base —— 带时间戳的自定义 ORM 基类（从 db_conf 迁移到这里）
   - 继承 DeclarativeBase，在类体里直接写 created_at / updated_at
   - 所有表类继承 Base 就自动带这俩字段，不用每个表重复写
2. Category 类 —— 对应数据库表 news_category

写法说明（SQLAlchemy 2.x）：
- 用 Mapped[类型] 做类型注解，mapped_column(...) 定义列
- SQL 列类型由 Mapped 的 Python 类型自动推断：int→Integer，str→String，datetime→DateTime
- 需要指定长度时才在 mapped_column 里显式写类型，如 mapped_column(String(32))
- 自定义基类用 class Base(DeclarativeBase)，不再用 Base = declarative_base()
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


# ↓↓↓ 第一步：定义带时间戳的自定义 Base ↓↓↓
#
# class Base(DeclarativeBase):
#     """带时间戳的 ORM 基类，所有表类继承它自动带 created_at / updated_at。"""
#     created_at: Mapped[datetime] = mapped_column(server_default=func.now(), comment="创建时间")
#     updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), comment="更新时间")
#
# 说明：
# - 用 class Base(DeclarativeBase) 而不是 Base = declarative_base()，
#   因为只有显式定义的类才能在类体里加公共字段让子类继承
# - created_at：插入时由数据库填当前时间（server_default=func.now()）
# - updated_at：插入时填当前时间 + 每次更新自动刷新（onupdate=func.now()）
#   方案 B：updated_at 真正名副其实，修改记录时会自动变成当前时间
# - 所有子表自动继承这两个字段，改一处全局生效


# ↓↓↓ 第二步：定义 Category 类，对应数据库表 news_category ↓↓↓
#
# 真实表结构（已对照数据库 DESCRIBE news_category）：
#   id          int unsigned   PRI, auto_increment
#   name        varchar(50)    UNI（唯一）, NOT NULL
#   sort_order  int            NOT NULL, 默认 0
#   created_at  timestamp      NOT NULL, 默认 CURRENT_TIMESTAMP          ← 从 Base 继承
#   updated_at  timestamp      NOT NULL, 默认 CURRENT_TIMESTAMP on update ← 从 Base 继承
#
# 写法模板（你来填）：
#
# class Category(Base):
#     __tablename__ = "news_category"        # 对应数据库里的真实表名
#
#     # 主键 id：Mapped[int] 自动推断为 Integer
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="分类ID")
#
#     # 分类名称：真实表 varchar(50) 且唯一，所以 String(50) + unique=True
#     name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
#
#     # 排序值：真实表 int, NOT NULL, 默认 0
#     # default=0 表示插入时不传值就用 0（固定常量用 default 即可，不必 server_default）
#     sort_order: Mapped[int] = mapped_column(default=0, nullable=False, comment="排序值")
#
#     # 注意：created_at / updated_at 不用在这里写，从 Base 自动继承过来
#
# 提示：
# - __tablename__ 必须和数据库里的真实表名完全一致（news_category）
# - Mapped[int] / Mapped[str] 是 Python 类型注解，SQLAlchemy 据此推断 SQL 列类型
# - primary_key=True 标记主键，autoincrement=True 自增
# - nullable=False 表示不能为空，unique=True 表示唯一约束
# - comment 是列注释，方便阅读表结构


# 重要：本文件不写 if __name__ == "__main__"，它是被其他模块 import 使用的。

class Base(DeclarativeBase):
    """带时间戳的 ORM 基类，所有表类继承它自动带 created_at / updated_at。"""
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), comment="更新时间")

class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False, comment="排序值")

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name}, sort_order={self.sort_order})"


# ↓↓↓ 第三步：定义 News 类，对应数据库表 news ↓↓↓
#
# 真实表结构（已对照数据库 DESCRIBE news）：
#   id            int unsigned    PRI, auto_increment
#   title         varchar(255)    NOT NULL
#   description   varchar(500)    YES（可空）
#   content       text            NOT NULL
#   image         varchar(255)    YES（可空）
#   author        varchar(50)     YES（可空）
#   category_id   int unsigned    NOT NULL, MUL（外键 → news_category.id）
#   views         int unsigned    NOT NULL, 默认 0
#   publish_time  timestamp       NOT NULL, MUL, 默认 CURRENT_TIMESTAMP
#   created_at    timestamp       NOT NULL, 默认 CURRENT_TIMESTAMP          ← 从 Base 继承
#   updated_at    timestamp       NOT NULL, 默认 CURRENT_TIMESTAMP on update ← 从 Base 继承
#
# 写法模板（你来填）：
#
# class News(Base):
#     __tablename__ = "news"               # 对应数据库里的真实表名
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="新闻ID")
#
#     # 标题：varchar(255) NOT NULL
#     title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
#
#     # 简介：varchar(500)，可空 → Optional[str]
#     description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
#
#     # 内容：text NOT NULL → 需要 import Text 并用 mapped_column(Text, ...)
#     content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
#
#     # 图片：varchar(255)，可空
#     image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片")
#
#     # 作者：varchar(50)，可空
#     author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
#
#     # 分类ID：int unsigned NOT NULL，外键关联 news_category.id
#     # 提示：foreign key 写法是 ForeignKey("news_category.id")
#     category_id: Mapped[int] = mapped_column(ForeignKey("news_category.id"), nullable=False, comment="分类ID")
#
#     # 浏览量：int unsigned NOT NULL，默认 0
#     views: Mapped[int] = mapped_column(default=0, nullable=False, comment="浏览量")
#
#     # 发布时间：timestamp NOT NULL, 默认 CURRENT_TIMESTAMP
#     # 需要 import TIMESTAMP 或用 server_default=func.now()
#     publish_time: Mapped[datetime] = mapped_column(server_default=func.now(), comment="发布时间")
#
#     # relationship 关联（可选）：通过 Category 对象访问，不用写进表里
#     # category: Mapped["Category"] = relationship(back_populates="news_list")
#
# 提示：
# - 可空字段用 Mapped[Optional[str]]，需要 from typing import Optional
# - Text 类型需要 from sqlalchemy import Text
# - ForeignKey 需要 from sqlalchemy import ForeignKey
# - relationship 需要 from sqlalchemy.orm import relationship（可选，先不做也行）
# - created_at / updated_at 从 Base 继承，不用写

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(ForeignKey("news_category.id"), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(server_default=func.now(), comment="发布时间")

    # 索引
    __table_args__ = (
        Index("idx_news_category_id", "category_id"),
        Index("idx_news_publish_time", "publish_time"),
    )

    def __repr__(self):
        return f"News(id={self.id}, title={self.title}, description={self.description}, content={self.content}, image={self.image}, author={self.author}, category_id={self.category_id}, views={self.views}, publish_time={self.publish_time})"