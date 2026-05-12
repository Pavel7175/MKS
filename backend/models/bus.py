import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .subscriber import Subscriber


class Bus(Base):
    __tablename__ = "buses"

    bus_type: Mapped[str] = mapped_column()  # Тип шины
    bus_count: Mapped[int] = mapped_column()  # Количество

    subscriber_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscribers.id"))
    subscriber: Mapped["Subscriber"] = relationship(back_populates="buses")
