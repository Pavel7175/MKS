from uuid import UUID

from pydantic import BaseModel

# --- ШИНЫ ---


class BusBase(BaseModel):
    bus_type: str
    bus_count: int


class BusCreate(BusBase):
    pass


class BusRead(BusBase):
    id: UUID

    class Config:
        from_attributes = True
