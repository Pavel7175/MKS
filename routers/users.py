from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from argon2 import PasswordHasher
from models import User
from database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])
ph = PasswordHasher()


@router.post("/users/create")
def create_user(
        username: str,
        password: str,
        session: Session = Depends(get_session)):
    # Проверка, нет ли уже такого юзера
    existing = session.exec(
        select(User).where(
            User.username == username)).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Пользователь уже существует")

    # Хешируем через Argon2
    hashed = ph.hash(password)
    new_user = User(username=username, password_hash=hashed, role="admin")
    session.add(new_user)
    session.commit()
    return {"ok": True}


@router.post("/login")
def login(
        username: str,
        password: str,
        session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return {"auth": False, "detail": "Пользователь не найден"}

    try:
        # Проверка пароля Argon2
        ph.verify(user.password_hash, password)
        return {"auth": True, "username": user.username, "role": user.role}
    except BaseException:
        return {"auth": False, "detail": "Неверный пароль"}
