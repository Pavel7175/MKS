from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Reference(Base):
    __tablename__ = "references"

    # 'TT', 'PU', 'Bus', 'Panel', 'USPD'
    category: Mapped[str] = mapped_column(index=True)
    # Название, например '200/5' или 'Меркурий 230'
    value: Mapped[str] = mapped_column(unique=True)
