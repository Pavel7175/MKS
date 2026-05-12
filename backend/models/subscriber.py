import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .bus import Bus
    from .section import Section


class Subscriber(Base):
    __tablename__ = "subscribers"

    number: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    fuse_rating: Mapped[str] = mapped_column()  # Номинал предохранителя
    cable_brand: Mapped[str] = mapped_column()  # Марка кабеля
    cable_length: Mapped[float] = mapped_column()

    # ТТ и ПУ
    ct_rating: Mapped[str] = mapped_column()  # Номинал ТТ
    ct_type: Mapped[str] = mapped_column()  # Тип ТТ
    meter_type: Mapped[str] = mapped_column()  # Тип ПУ

    # Связи
    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sections.id"))
    section: Mapped["Section"] = relationship(back_populates="subscribers")

    buses: Mapped[list["Bus"]] = relationship(
        back_populates="subscriber",
        cascade="all, delete-orphan",  # УДАЛЯТЬ ВСЕХ ДЕТЕЙ
    )
