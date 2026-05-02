from sqlmodel import SQLModel, create_engine, Session
# Импортируем модели, чтобы SQLModel зарегистрировал их в метаданных
from models import TP, Section, Subscriber, Bus, Reference  # noqa

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_and_tables():
    # Теперь эта команда создаст все таблицы: tp, section, subscriber и bus
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
