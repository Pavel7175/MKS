import pandas as pd
from sqlmodel import Session, select
from database import engine
from models import TP


def export_to_excel(file_name="tp_export.xlsx"):
    with Session(engine) as session:
        # Загружаем все ТП со всеми связями
        statement = select(TP)
        tps = session.exec(statement).all()

        flattened_data = []

        for tp in tps:
            for sec in tp.sections:
                for sub in sec.subscribers:
                    # Если шин нет, создаем одну строку для абонента
                    buses = sub.buses if sub.buses else [None]
                    for bus in buses:
                        row = {
                            "№ ТП": tp.tp_number,
                            "Район": tp.district,
                            "Адрес ТП": tp.address,
                            "Напряжение": tp.voltage,
                            "Луч": sec.number,
                            "Тип сборки": sec.assembly_type,
                            "Абонент": sub.name,
                            "Адрес абонента": sub.address,
                            "Предохранитель": sub.fuse_rating,
                            "Кабель": sub.cable_brand,
                            "Длина (м)": sub.cable_length,
                            "Тип шины": bus.bus_type if bus else "-",
                            "Кол-во шин": bus.bus_count if bus else 0
                        }
                        flattened_data.append(row)

        df = pd.DataFrame(flattened_data)
        df.to_excel(file_name, index=False)
        print(f"✅ Данные успешно выгружены в {file_name}")


if __name__ == "__main__":
    export_to_excel()
