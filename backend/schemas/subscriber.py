from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .bus import BusCreate, BusRead


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
    id: UUID
    buses: List[BusRead] = []


class SubscriberUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    fuse_rating: Optional[str] = None
    cable_brand: Optional[str] = None
    cable_length: Optional[float] = None
    ct_rating: Optional[str] = None
    ct_type: Optional[str] = None
    meter_type: Optional[str] = None
