from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .section import Section
    from .tp import TP


class TP(Base):
    __tablename__ = "tps"

    tp_number: Mapped[str] = mapped_column(index=True, unique=True)
    district: Mapped[str] = mapped_column()
    region: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    voltage: Mapped[str] = mapped_column()
    execution_type: Mapped[str] = mapped_column()

    # Необязательные поля
    commissioning_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    transformer_type: Mapped[str] = mapped_column()
    uspd_type: Mapped[str] = mapped_column()
    docs_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    maps_nn: Mapped[Optional[str]] = mapped_column(nullable=True)

    # Связи (Relationship)
    sections: Mapped[list["Section"]] = relationship(
        back_populates="tp", cascade="all, delete-orphan"
    )
