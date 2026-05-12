from uuid import UUID

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    id: UUID
    username: str
    password_hash: str
    nickname: str
    role: str
