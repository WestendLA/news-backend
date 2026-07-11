"""浏览历史数据模型。"""
from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="历史记录ID")
    user_id: Mapped[int] = mapped_column(nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(nullable=False, comment="新闻ID")
    view_time: Mapped[str] = mapped_column(nullable=False, comment="浏览时间")

    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
        Index("idx_view_time", "view_time"),
    )

    def __repr__(self):
        return f"History(id={self.id}, user_id={self.user_id}, news_id={self.news_id})"
