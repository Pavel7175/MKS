from sqlalchemy import event
from sqlalchemy.engine import Engine
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


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
