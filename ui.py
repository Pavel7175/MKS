import streamlit as st
import requests
import base64

st.set_page_config(layout="wide")
st.title("Просмотр схем ТП (.vsd, .vsdx)")

uploaded_file = st.file_uploader("Загрузите файл Visio", type=["vsd", "vsdx"])

if uploaded_file:
    with st.spinner("Конвертируем схему в PDF..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        # Убедитесь, что FastAPI запущен на порту 8000
        response = requests.post(
            "http://127.0.0.1:8000/visio/view",
            files=files,
            timeout=90)

        if response.status_code == 200:
            # Отображаем PDF через base64, так как это надежнее для браузера
            base64_pdf = base64.b64encode(response.content).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error(f"Ошибка: {response.text}")
