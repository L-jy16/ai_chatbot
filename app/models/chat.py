"""Stored question and answer, owned by one authenticated user."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(10), nullable=False)
    # mode 번호 체계. 1: 이전 계획서 번호(q4=타이밍, q5=새로운 각도, q6=다음 편),
    # 2: 화면(D)의 Q1~Q5 번호(현재), 3: C 재통합 중 쓰인 번호(1과 같은 의미)
    scenario_version: Mapped[int] = mapped_column(default=2, server_default="2", nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
