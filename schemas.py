from typing import Optional
from typing import Optional, List
from pydantic import BaseModel
from datetime import date

# --- ШИНЫ ---


class BusBase(BaseModel):
    bus_type: str
    bus_count: int


class BusCreate(BusBase):
    pass


class BusRead(BusBase):
    id: int

# --- АБОНЕНТЫ ---


class SubscriberBase(BaseModel):
    number: str
    name: str
    address: str
    fuse_rating: str
    cable_brand: str
    cable_length: float
    ct_rating: str
    ct_type: str
    meter_type: str


class SubscriberCreate(SubscriberBase):
    buses: List[BusCreate] = []  # Абонент создается со списком шин


class SubscriberRead(SubscriberBase):
    id: int
    buses: List[BusRead] = []

# --- СЕКЦИИ ---


class SectionBase(BaseModel):
    number: str
    assembly_type: str
    panel: str


class SectionCreate(SectionBase):
    subscribers: List[SubscriberCreate] = []  # Секция со списком абонентов


class SectionRead(SectionBase):
    id: int
    subscribers: List[SubscriberRead] = []

# --- ТП ---


class TPBase(BaseModel):
    tp_number: str
    district: str
    region: str
    address: str
    voltage: str
    execution_type: str
    transformer_type: str
    uspd_type: str
    commissioning_date: Optional[date] = None


class TPCreate(TPBase):
    sections: List[SectionCreate] = []  # ТП создается со всеми вложениями


class TPRead(TPBase):
    id: int
    sections: List[SectionRead] = []


class TPUpdate(BaseModel):
    tp_number: Optional[str] = None
    district: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    voltage: Optional[str] = None
    execution_type: Optional[str] = None
    transformer_type: Optional[str] = None
    uspd_type: Optional[str] = None
    commissioning_date: Optional[date] = None


class SubscriberUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    fuse_rating: Optional[str] = None
    cable_brand: Optional[str] = None
    cable_length: Optional[float] = None
    ct_rating: Optional[str] = None
    ct_type: Optional[str] = None
    meter_type: Optional[str] = None
