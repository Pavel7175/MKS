from schemas import TPUpdate
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import TP, Section, Subscriber, Bus
from schemas import TPCreate, TPRead
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import TP, Section, Subscriber, Bus
from schemas import TPUpdate, TPRead, TPRead, TPUpdate

router = APIRouter(prefix="/tps", tags=["Трансформаторные подстанции"])


@router.post("/", response_model=TPRead)
def create_tp(tp_data: TPCreate, session: Session = Depends(get_session)):
    # 1. Создаем объект ТП
    db_tp = TP(**tp_data.dict(exclude={"sections"}))

    # 2. Обходим секции
    for sec_data in tp_data.sections:
        db_section = Section(
            **sec_data.dict(exclude={"subscribers"}),
            tp=db_tp)
        session.add(db_section)

        # 3. Обходим абонентов
        for sub_data in sec_data.subscribers:
            db_subscriber = Subscriber(
                **sub_data.dict(exclude={"buses"}),
                section=db_section)
            session.add(db_subscriber)

            # 4. Обходим шины
            for bus_data in sub_data.buses:
                db_bus = Bus(**bus_data.dict(), subscriber=db_subscriber)
                session.add(db_bus)

    session.add(db_tp)
    session.commit()
    session.refresh(db_tp)
    return db_tp


@router.get("/", response_model=list[TPRead])
def read_tps(session: Session = Depends(get_session)):
    # select(TP) автоматически подтянет вложенные данные благодаря Relationship
    tps = session.exec(select(TP)).all()
    return tps


@router.delete("/{tp_id}")
def delete_tp(tp_id: int, session: Session = Depends(get_session)):
    tp = session.get(TP, tp_id)
    if not tp:
        raise HTTPException(status_code=404, detail="ТП не найдена")

    # SQLModel сам удалит вложенные данные, если настроен cascade (по
    # умолчанию в SQLite это нужно проверять)
    session.delete(tp)
    session.commit()
    return {"message": f"ТП {tp.tp_number} и все связанные данные удалены"}


@router.get("/by-number/{tp_number}", response_model=TPRead)
def read_tp_by_number(tp_number: str, session: Session = Depends(get_session)):
    # Ищем ТП в базе по номеру
    statement = select(TP).where(TP.tp_number == tp_number)
    results = session.exec(statement)
    tp = results.first()

    if not tp:
        raise HTTPException(status_code=404,
                            detail=f"ТП с номером {tp_number} не найдена")

    return tp


@router.patch("/{tp_id}", response_model=TPRead)
def update_tp(
        tp_id: int,
        tp_data: dict,
        session: Session = Depends(get_session)):
    db_tp = session.get(TP, tp_id)
    if not db_tp:
        raise HTTPException(status_code=404, detail="ТП не найдена")

    # Обновляем поля самой ТП
    for key, value in tp_data.items():
        if key != "sections" and hasattr(db_tp, key):
            setattr(db_tp, key, value)

    # Перезаписываем вложенную структуру
    if "sections" in tp_data:
        for old_sec in db_tp.sections:
            session.delete(old_sec)
        session.flush()

        for s_data in tp_data["sections"]:
            subs = s_data.pop("subscribers", [])
            s_data.pop("id", None)  # Убираем старый ID для новой вставки
            db_sec = Section(**s_data, tp=db_tp)
            session.add(db_sec)

            for sub_data in subs:
                buses = sub_data.pop("buses", [])
                sub_data.pop("id", None)
                db_sub = Subscriber(**sub_data, section=db_sec)
                session.add(db_sub)

                for b_data in buses:
                    b_data.pop("id", None)
                    db_bus = Bus(**b_data, subscriber=db_sub)
                    session.add(db_bus)

    session.commit()
    session.refresh(db_tp)
    return db_tp
