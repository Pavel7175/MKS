from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Task  # Убедись, что добавил Task в models.py

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/")
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


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
