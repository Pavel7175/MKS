from typing import Optional
from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel


class TaskBase(SQLModel):
    tp_number: str
    district: str

    @field_validator("tp_number", "district")
    @classmethod
    def validate_numbers(cls, v: str):
        if not v.isdigit():
            raise ValueError("Должны быть только цифры")
        return v


class TaskCreate(TaskBase):
    executor: Optional[str] = None
    deadline: str
    nickname: str
    comment: Optional[str] = None
    ppo_report: Optional[str] = None
    status: str


class TaskRead(TaskBase):
    id: UUID
    nickname: str
    executor: str
    deadline: str
    comment: str
    ppo_report: str
    status: str

    class Config:
        from_attributes = True


class TaskUpdate(SQLModel):
    tp_number: Optional[str] = None
    district: Optional[str] = None
    nickname: Optional[str] = None
    deadline: Optional[str] = None
    comment: Optional[str] = None
    ppo_report: Optional[str] = None
    status: Optional[str] = None
