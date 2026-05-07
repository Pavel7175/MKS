from fastapi import FastAPI

from database import create_db_and_tables, init_admin
from routers import buses, refs, sections, subscribers, task, tp, users, visio

app = FastAPI(title="MKS API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    init_admin()


# Регистрируем роутер
app.include_router(tp.router)
app.include_router(sections.router)
app.include_router(subscribers.router)
app.include_router(buses.router)
app.include_router(refs.router)
app.include_router(task.router)
app.include_router(users.router)
app.include_router(visio.router)


@app.get("/")
def read_root():
    return {"message": "Система учета ТП работает"}


