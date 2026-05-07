import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from database import get_session
from models import User

# --- Конфигурация ---
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

router = APIRouter(prefix="/auth", tags=["Auth"])
ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Вспомогательные функции ---

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Доступ запрещен: нужны права администратора")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Невалидный или просроченный токен")

# --- Эндпоинты ---

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    # Теперь достаем данные из form_data
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()
    
    if not user or not ph.verify(user.password_hash, form_data.password):
        raise HTTPException(
            status_code=401, 
            detail="Ошибка входа: неверное имя или пароль"
        )
    
    token = create_access_token({"sub": user.username, "role": user.role})
    return {
        "access_token": token,  # Важно: Swagger ищет именно этот ключ
        "token_type": "bearer",
        "username": user.username, 
        "role": user.role
    }

@router.post("/users/create")
def create_user(
    username: str, 
    password: str, 
    admin_data: dict = Depends(get_current_admin), # Только для админов
    session: Session = Depends(get_session)
):
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = User(username=username, password_hash=ph.hash(password), role="user")
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.get("/users")
def get_all_users(
    admin_data: dict = Depends(get_current_admin), # Только для админов
    session: Session = Depends(get_session)
):
    return session.exec(select(User)).all()

@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int, 
    new_role: str, 
    admin_data: dict = Depends(get_current_admin), # Только для админов
    session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    db_user.role = new_role
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int, 
    admin_data: dict = Depends(get_current_admin), # Только для админов
    session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    session.delete(db_user)
    session.commit()
    return {"ok": True}
