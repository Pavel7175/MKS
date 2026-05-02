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
from schemas import TPUpdate, TPRead
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

    # Обновляем основные поля ТП
    for key, value in tp_data.items():
        if key != "sections" and hasattr(db_tp, key):
            setattr(db_tp, key, value)

    # Работа со вложенными данными
    if "sections" in tp_data:
        # 1. Удаляем абсолютно все старые связи этой ТП (каскадно)
        # Это гарантирует, что старые данные не "всплывут"
        for section in db_tp.sections:
            session.delete(section)
        session.flush()

        # 2. Записываем новые данные из формы
        for sec_data in tp_data["sections"]:
            subs_data = sec_data.pop("subscribers", [])
            new_sec = Section(**sec_data, tp=db_tp)
            session.add(new_sec)

            for sub_data in subs_data:
                buses_data = sub_data.pop("buses", [])
                new_sub = Subscriber(**sub_data, section=new_sec)
                session.add(new_sub)

                for bus_data in buses_data:
                    new_bus = Bus(**bus_data, subscriber=new_sub)
                    session.add(new_bus)

    session.commit()
    session.refresh(db_tp)  # Обновляем объект из базы перед возвратом
    return db_tp
