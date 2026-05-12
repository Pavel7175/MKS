from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .section import SectionCreate, SectionRead

# --- ТП ---


class TPBase(BaseModel):
    # id: UUID
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
    id: UUID
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
