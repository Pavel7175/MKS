import streamlit as st
import pandas as pd
import requests
from io import BytesIO

API_URL = "http://127.0.0.1:8000"

st.title("📊 Экспорт данных")

if st.button("📥 Сформировать Excel"):
    res = requests.get(f"{API_URL}/tps/")
    if res.status_code == 200:
        # Здесь логика развертывания JSON в плоскую таблицу (как в export_tool.py)
        # Для примера просто выгрузим список ТП
        df = pd.DataFrame(res.json())
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            label="💾 Скачать .xlsx",
            data=output.getvalue(),
            file_name="mks_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
