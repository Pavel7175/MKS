import logging
from datetime import date  # Добавь в начало файла
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import TP, Section, Subscriber, Bus
from schemas import TPCreate, TPRead
from fastapi import HTTPException
from utils import sync_references
from sqlmodel import desc
from sqlalchemy.exc import IntegrityError
router = APIRouter(prefix="/tps", tags=["Трансформаторные подстанции"])


@router.post("/", response_model=TPRead)
def create_tp(tp_data: TPCreate, session: Session = Depends(get_session)):
    # 1. ПРОВЕРКА НА ДУБЛИКАТ (перед созданием)
    existing_tp = session.exec(select(TP).where(
        TP.tp_number == tp_data.tp_number)).first()
    if existing_tp:
        raise HTTPException(
            status_code=400,
            detail=f"ТП с номером {tp_data.tp_number} уже существует в базе!"
        )

    try:
        # Твой текущий код создания объектов (как на скрине)
        # 1. Создаем объект ТП
        sync_references(tp_data.dict(), session)
        db_tp = TP(**tp_data.dict(exclude={"sections"}))

        # 2. Обходим секции
        for sec_data in tp_data.sections:
            db_section = Section(
                **sec_data.dict(exclude={"subscribers"}),
                tp=db_tp
            )
            session.add(db_section)

            # 3. Обходим абонентов
            for sub_data in sec_data.subscribers:
                db_subscriber = Subscriber(
                    **sub_data.dict(exclude={"buses"}),
                    section=db_section
                )
                session.add(db_subscriber)

                # 4. Обходим шины
                for bus_data in sub_data.buses:
                    db_bus = Bus(**bus_data.dict(), subscriber=db_subscriber)
                    session.add(db_bus)

        session.add(db_tp)
        session.commit()
        session.refresh(db_tp)
        return db_tp

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ошибка целостности данных (возможно, дубликат)")


@router.get("/", response_model=list[TPRead])
def read_tps(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = 20
):
    # Добавляем принудительную сортировку по ID
    statement = select(TP).order_by(desc(TP.id)).offset(offset).limit(limit)

    tps = session.exec(statement).all()
    return tps


@router.delete("/{tp_id}")
def delete_tp(tp_id: int, session: Session = Depends(get_session)):
    try:
        tp = session.get(TP, tp_id)
        if not tp:
            raise HTTPException(status_code=404, detail="ТП не найдена")

        # Явное удаление (чтобы обойти проблемы с SQLite)
        session.delete(tp)
        session.commit()
        return {"message": "Удалено успешно"}

    except IntegrityError as e:
        session.rollback()
        logging.error(f"ОШИБКА СВЯЗЕЙ БД: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Нельзя удалить: есть связанные данные. Ошибка: {str(e)}")
    except Exception as e:
        session.rollback()
        logging.error(f"ОБЩАЯ ОШИБКА: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    sync_references(tp_data, session)
    db_tp = session.get(TP, tp_id)
    if not db_tp:
        raise HTTPException(status_code=404, detail="ТП не найдена")

    # 1. Обработка даты (конвертация строки в объект date)
    if "commissioning_date" in tp_data and isinstance(
        tp_data
        ["commissioning_date"],
            str):
        try:
            tp_data["commissioning_date"] = date.fromisoformat(
                tp_data["commissioning_date"])
        except ValueError:
            pass

    # 2. Обновляем основные поля ТП
    for key, value in tp_data.items():
        if key != "sections" and hasattr(db_tp, key):
            setattr(db_tp, key, value)

    # 3. Полная перезапись структуры секций, абонентов и шин
    if "sections" in tp_data:
        # УДАЛЕНИЕ: Чистим всё старое дерево связей этой ТП
        for section in db_tp.sections:
            for sub in section.subscribers:
                for bus in sub.buses:
                    session.delete(bus)
                session.delete(sub)
            session.delete(section)

        # Сбрасываем изменения в БД перед вставкой новых данных
        session.flush()

        # ВСТАВКА: Создаем новую структуру с чистого листа
        for s_data in tp_data["sections"]:
            subs_data = s_data.pop("subscribers", [])
            s_data.pop("id", None)  # Игнорируем старые ID

            db_section = Section(**s_data, tp=db_tp)
            session.add(db_section)
            session.flush()  # Получаем новый ID секции

            for sub_data in subs_data:
                buses_data = sub_data.pop("buses", [])
                sub_data.pop("id", None)  # Игнорируем старые ID

                db_subscriber = Subscriber(
                    **sub_data, section_id=db_section.id)
                session.add(db_subscriber)
                session.flush()  # Получаем новый ID абонента

                for bus_data in buses_data:
                    bus_data.pop("id", None)  # Игнорируем старые ID
                    db_bus = Bus(**bus_data, subscriber_id=db_subscriber.id)
                    session.add(db_bus)

    # 4. Финальное сохранение
    session.commit()
    session.refresh(db_tp)
    return db_tp


@router.get("/check-number/{tp_number}")
def check_tp_number(tp_number: str, session: Session = Depends(get_session)):
    statement = select(TP).where(TP.tp_number == tp_number)
    exists = session.exec(statement).first() is not None
    return {"exists": exists}
