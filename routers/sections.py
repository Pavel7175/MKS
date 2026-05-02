from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Section
from schemas import SectionCreate, SectionRead

router = APIRouter(prefix="/sections", tags=["Секции (Лучи)"])


@router.post("/", response_model=SectionRead)
def create_section(section_data: SectionCreate, tp_id: int,
                   session: Session = Depends(get_session)):
    # Создаем секцию, привязывая её к конкретной ТП
    db_section = Section(
        **section_data.dict(exclude={"subscribers"}),
        tp_id=tp_id)
    session.add(db_section)
    session.commit()
    session.refresh(db_section)
    return db_section


@router.get("/{section_id}", response_model=SectionRead)
def read_section(section_id: int, session: Session = Depends(get_session)):
    section = session.get(Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Секция не найдена")
    return section
