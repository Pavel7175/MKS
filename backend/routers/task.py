from datetime import date
from typing import List
from uuid import UUID

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import TP, Task
from schemas.task import TaskCreate, TaskRead, TaskUpdate
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead)  # Лучше возвращать TaskRead (с ID)
def create_task(task_in: TaskCreate, session: Session = Depends(get_session)):

    statement = select(func.count(Task.id)).where(Task.deadline == task_in.deadline)
    count = session.exec(statement).one()
    if count >= 15:
        raise HTTPException(
            status_code=400,
            detail=f"На дату {task_in.deadline} уже назначено 15 заявок. Лимит исчерпан.",
        )

    # 1. Проверка формата (если не добавил validator в саму схему)
    if not task_in.tp_number.isdigit():
        raise HTTPException(
            status_code=400, detail="Номер ТП должен состоять только из цифр"
        )

    # 2. Проверка в основной базе ТП (таблица TP)
    # Замени TP на имя твоей модели основной базы
    existing_tp = session.exec(
        select(TP).where(TP.tp_number == task_in.tp_number)
    ).first()
    if existing_tp:
        raise HTTPException(
            status_code=400, detail=f"ТП {task_in.tp_number} уже есть в основной базе!"
        )

    # 3. Проверка в текущих заявках (таблица Task)
    existing_task = session.exec(
        select(Task).where(Task.tp_number == task_in.tp_number)
    ).first()
    if existing_task:
        raise HTTPException(
            status_code=400, detail="Эта ТП уже добавлена в план заявок"
        )

    if task_in.deadline:
        try:
            deadline_date = date.fromisoformat(task_in.deadline)
            if deadline_date < date.today():
                raise HTTPException(
                    status_code=400, detail="Нельзя создавать в прошлом"
                )
        except ValueError:
            raise HTTPException(status_code=400, detail="Некорректный формат даты")

    # Проверка: дата не может быть раньше сегодняшней
    if deadline_date < date.today():
        raise HTTPException(
            status_code=400, detail="Нельзя создавать заявку на прошедшую дату"
        )
    try:
        # task = Task.model_validate(task_in) # Более современный способ SQLModel
        task = Task(**task_in.model_dump())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка БД: {e.orig}")
        # raise HTTPException(status_code=400, detail="Ошибка уникальности данных в БД")


@router.get("/", response_model=List[TaskRead])
def read_tasks(session: Session = Depends(get_session)):
    statement = select(Task).order_by(Task.deadline)
    return session.exec(statement).all()


@router.delete("/{task_id}")
def delete_task(task_id: UUID, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    session.delete(task)
    session.commit()
    return {"ok": True}


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: UUID, task_data: TaskUpdate, session: Session = Depends(get_session)
):
    # 1. Достаем объект из БД
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    # 2. Превращаем пришедшие данные в словарь, исключая пустые (None)
    update_data = task_data.model_dump(exclude_unset=True)

    # 3. Применяем изменения к объекту из БД
    for key, value in update_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/tasks/check-exists/{tp_number}")
def check_task_exists(tp_number: str, session: Session = Depends(get_session)):
    # Ищем именно в таблице ЗАЯВОК (Task)
    task = session.exec(select(Task).where(Task.tp_number == tp_number)).first()
    return {"exists": task is not None}
