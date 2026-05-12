from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .subscriber import Subscriber
    from .tp import TP


class Section(Base):
    __tablename__ = "sections"

    number: Mapped[str] = mapped_column()
    assembly_type: Mapped[str] = mapped_column()  # Тип сборки
    panel: Mapped[str] = mapped_column()  # Панель

    tp_id: Mapped[UUID] = mapped_column(ForeignKey("tps.id"))
    tp: Mapped["TP"] = relationship(back_populates="sections")
    subscribers: Mapped[list["Subscriber"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",  # УДАЛЯТЬ ВСЕХ ДЕТЕЙ
    )
