from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Task, TaskUpdate
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/")
def create_task(task: Task, session: Session = Depends(get_session)):
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Такой номер ТП уже есть в заявках")



@router.get("/")
def read_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@router.delete("/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    session.delete(task)
    session.commit()
    return {"ok": True}

@router.patch("/{task_id}", response_model=Task)
def patch_task(
    task_id: int, 
    task_data: TaskUpdate, 
    session: Session = Depends(get_session)
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