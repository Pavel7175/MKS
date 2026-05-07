import os

from argon2 import PasswordHasher
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

# Импортируем модели, чтобы SQLModel зарегистрировал их в метаданных
from models import (  # noqa
    TP,
    Bus,
    Reference,
    Section,
    Subscriber,
    User,  # Убедись, что путь к модели User верный
)

load_dotenv()
# Создаем объект ph, у которого есть метод .hash()
ph = PasswordHasher()

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_and_tables():
    # Теперь эта команда создаст все таблицы: tp, section, subscriber и bus
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



def init_admin():
    # Данные берутся из переменных окружения (которые Streamlit прокидывает из secrets)
    admin_login = os.getenv("ADMIN_LOGIN", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    with Session(engine) as session:
        # Проверяем наличие любого пользователя с ролью admin
        statement = select(User).where(User.role == "admin")
        existing_admin = session.exec(statement).first()

        if not existing_admin:
            print(f"🚀 Создание администратора '{admin_login}'...")
            hashed_pw = ph.hash(admin_password)
            new_admin = User(
                username=admin_login,
                password_hash=hashed_pw,
                role="admin"
            )
            session.add(new_admin)
            session.commit()
            print("✅ Администратор успешно создан.")
        else:
            print("ℹ️ Администратор уже есть в базе.")
