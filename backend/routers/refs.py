from typing import List

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Reference
from sqlmodel import Session, select

router = APIRouter(prefix="/refs", tags=["Справочники"])


# Указываем, что возвращаем список СТРОК
@router.get("/{category}", response_model=List[str])
def get_refs(category: str, session: Session = Depends(get_session)):
    # Выбираем только колонку .value, а не весь объект
    statement = select(
        Reference.value).where(
        Reference.category == category.upper())
    results = session.exec(statement).all()
    return results


@router.post("/")
def add_ref(data: dict, session: Session = Depends(get_session)):
    # Проверка на существование, чтобы не плодить дубликаты
    existing = session.exec(select(Reference).where(
        Reference.category == data["category"].upper(),
        Reference.value == data["value"]
    )).first()

    if existing:
        return {"ok": True, "message": "Already exists"}

    new_ref = Reference(category=data["category"].upper(), value=data["value"])
    session.add(new_ref)
    session.commit()
    return {"ok": True}


@router.delete("/{category}/{value}")
def delete_ref(
        category: str,
        value: str,
        session: Session = Depends(get_session)):
    statement = select(Reference).where(
        Reference.category == category.upper(),
        Reference.value == value
    )
    res = session.exec(statement).first()
    if res:
        session.delete(res)
        session.commit()
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Value not found")
