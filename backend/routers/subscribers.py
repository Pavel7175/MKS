from uuid import UUID

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Subscriber
from schemas import SubscriberCreate, SubscriberRead, SubscriberUpdate
from sqlmodel import Session

router = APIRouter(prefix="/subscribers", tags=["Абоненты"])


@router.post("/", response_model=SubscriberRead)
def create_subscriber(
    sub_data: SubscriberCreate,
    section_id: UUID,
    session: Session = Depends(get_session),
):
    # Привязываем абонента к секции
    db_sub = Subscriber(**sub_data.dict(exclude={"buses"}), section_id=section_id)
    session.add(db_sub)
    session.commit()
    session.refresh(db_sub)
    return db_sub


@router.get("/{sub_id}", response_model=SubscriberRead)
def read_subscriber(sub_id: UUID, session: Session = Depends(get_session)):
    sub = session.get(Subscriber, sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Абонент не найден")
    return sub


@router.patch("/{sub_id}", response_model=SubscriberRead)
def update_subscriber(
    sub_id: UUID, sub_data: SubscriberUpdate, session: Session = Depends(get_session)
):
    db_sub = session.get(Subscriber, sub_id)
    if not db_sub:
        raise HTTPException(status_code=404, detail="Абонент не найден")

    new_data = sub_data.dict(exclude_unset=True)
    for key, value in new_data.items():
        setattr(db_sub, key, value)

    session.add(db_sub)
    session.commit()
    session.refresh(db_sub)
    return db_sub
