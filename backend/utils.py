from models import Reference
from sqlmodel import Session, select


def sync_references(data: dict, session: Session):
    """
    Автоматически добавляет новые значения в справочники.
    Сканирует данные ТП и сохраняет типы УСПД, ТТ, ПУ и т.д.
    """
    # Карта соответствия полей JSON категориям справочника
    ref_map = {
        "uspd_type": "USPD",
        "ct_type": "TT_TYPE",
        "ct_rating": "TT_RATING",
        "meter_type": "PU_TYPE",
        "panel": "PANEL",
        "bus_type": "BUS_TYPE",
        "assembly_type": "ASSEMBLY",
    }

    def process_node(node):
        if isinstance(node, dict):
            for key, value in node.items():
                # Если ключ есть в нашей карте и значение не пустое
                if key in ref_map and value and isinstance(value, str):
                    category = ref_map[key]
                    # Проверяем наличие значения в БД
                    statement = select(Reference).where(
                        Reference.category == category,
                        Reference.value == value
                    )
                    exists = session.exec(statement).first()

                    if not exists:
                        new_ref = Reference(category=category, value=value)
                        session.add(new_ref)

                # Идем глубже (в секции, абоненты и т.д.)
                process_node(value)

        elif isinstance(node, list):
            for item in node:
                process_node(item)

    process_node(data)
    # session.flush() гарантирует, что ID для новых refs созданы,
    # но не закрывает транзакцию (commit будет в роутере)
    session.flush()
