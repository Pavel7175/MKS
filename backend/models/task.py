from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Task(Base):
    __tablename__ = "tasks"
    tp_number: Mapped[str] = mapped_column(index=True, unique=True)
    district: Mapped[str] = mapped_column()
    executor: Mapped[str] = mapped_column()
    nickname: Mapped[str] = mapped_column()
    deadline: Mapped[Optional[str]] = mapped_column(nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(nullable=True)
    ppo_report: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column()
