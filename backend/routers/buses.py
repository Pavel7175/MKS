from uuid import UUID

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Bus
from schemas import BusCreate, BusRead
from sqlmodel import Session

router = APIRouter(prefix="/buses", tags=["Шины"])


@router.post("/", response_model=BusRead)
def create_bus(
    bus_data: BusCreate, subscriber_id: UUID, session: Session = Depends(get_session)
):
    """Добавляет новую шину к абоненту."""
    db_bus = Bus(**bus_data.dict(), subscriber_id=subscriber_id)
    session.add(db_bus)
    session.commit()
    session.refresh(db_bus)
    return db_bus


@router.delete("/{bus_id}")
def delete_bus(bus_id: UUID, session: Session = Depends(get_session)):
    """Удаляет шину у абонента."""
    bus = session.get(Bus, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Шина не найдена")
    session.delete(bus)
    session.commit()
    return {"ok": True}
