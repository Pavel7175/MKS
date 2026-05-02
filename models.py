from typing import List, Optional
from datetime import date
from sqlmodel import Field, Relationship, SQLModel

# 1. Шины (т.к. у одного абонента их может быть несколько разных типов)


class Bus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bus_type: str  # Тип шины
    bus_count: int  # Количество

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: "Subscriber" = Relationship(back_populates="buses")

# 2. Абонент


class Subscriber(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    name: str
    address: str
    fuse_rating: str  # Номинал предохранителя
    cable_brand: str  # Марка кабеля
    cable_length: float

    # ТТ и ПУ
    ct_rating: str  # Номинал ТТ
    ct_type: str    # Тип ТТ
    meter_type: str  # Тип ПУ

    # Связи
    section_id: int = Field(foreign_key="section.id")
    section: "Section" = Relationship(back_populates="subscribers")
    buses: List[Bus] = Relationship(back_populates="subscriber")

# 3. Секция (Луч)


class Section(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    assembly_type: str  # Тип сборки
    panel: str         # Панель

    tp_id: int = Field(foreign_key="tp.id")
    tp: "TP" = Relationship(back_populates="sections")
    subscribers: List[Subscriber] = Relationship(back_populates="section")

# 4. ТП (Трансформаторная подстанция)


class TP(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tp_number: str = Field(unique=True, index=True)  # Уникальный номер ТП
    district: str  # Район
    region: str    # Округ
    address: str
    voltage: str   # Напряжение
    execution_type: str
    commissioning_date: Optional[date] = None
    transformer_type: str
    uspd_type: str  # Тип УСПД

    sections: List["Section"] = Relationship(
        back_populates="tp",
        cascade_delete=True
    )
