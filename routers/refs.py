from models import Reference
from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Reference  # Нужно добавить в models.py
from typing import List

router = APIRouter(prefix="/refs", tags=["Справочники"])

# Получить все значения конкретной категории


@router.get("/{category}", response_model=List[str])
def get_refs_by_category(
        category: str,
        session: Session = Depends(get_session)):
    statement = select(
        Reference.value).where(
        Reference.category == category.upper())
    results = session.exec(statement).all()
    return results

# Добавить новое значение в справочник


@router.post("/")
def add_ref_item(item_data: dict, session: Session = Depends(get_session)):
    # Проверка на дубликаты
    existing = session.exec(select(Reference).where(
        Reference.category == item_data["category"].upper(),
        Reference.value == item_data["value"]
    )).first()

    if existing:
        raise HTTPException(status_code=400, detail="Такое значение уже есть")

    new_item = Reference(
        category=item_data["category"].upper(),
        value=item_data["value"])
    session.add(new_item)
    session.commit()
    return {"ok": True}

# Удалить значение


@router.delete("/{ref_id}")
def delete_ref_item(ref_id: int, session: Session = Depends(get_session)):
    item = session.get(Reference, ref_id)
    if not item:
        raise HTTPException(status_code=404, detail="Не найдено")
    session.delete(item)
    session.commit()
    return {"ok": True}


@router.get("/{category}", response_model=List[str])
def get_refs(category: str, session: Session = Depends(get_session)):
    # Возвращаем только список строк-значений
    statement = select(
        Reference.value).where(
        Reference.category == category.upper())
    return session.exec(statement).all()


@router.post("/")
def add_ref(data: dict, session: Session = Depends(get_session)):
    new_ref = Reference(category=data["category"].upper(), value=data["value"])
    session.add(new_ref)
    session.commit()
    return {"ok": True}


@router.delete("/{category}/{value}")
def delete_ref_by_value(
        category: str,
        value: str,
        session: Session = Depends(get_session)):
    statement = select(Reference).where(
        Reference.category == category.upper(),
        Reference.value == value
    )
    item = session.exec(statement).first()
    if item:
        session.delete(item)
        session.commit()
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Не найдено")


router = APIRouter(prefix="/refs", tags=["Справочники"])
