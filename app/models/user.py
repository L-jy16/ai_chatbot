from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"
    # SQLite는 기본적으로 지운 마지막 id를 재사용한다. 그러면 삭제된 사용자의 세션 쿠키가
    # 새 가입자로 인식되므로, AUTOINCREMENT로 id 재사용을 막는다.
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # UTC
