from typing import List
from uuid import UUID

from pydantic import BaseModel

from .subscriber import SubscriberCreate, SubscriberRead

# --- СЕКЦИИ ---


class SectionBase(BaseModel):
    number: str
    assembly_type: str
    panel: str


class SectionCreate(SectionBase):
    subscribers: List[SubscriberCreate] = []  # Секция со списком абонентов


class SectionRead(SectionBase):
    id: UUID
    subscribers: List[SubscriberRead] = []
