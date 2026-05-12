from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    nickname: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column(default="user")  # "admin" или "user"
