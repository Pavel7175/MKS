import streamlit as st
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"


def login_page():
    st.title("🔐 Вход в систему МКС")
    with st.form("login_form"):
        user = st.text_input("Логин")
        pw = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            res = requests.post(
                f"{API_URL}/auth/login",
                params={
                    "username": user,
                    "password": pw})
            data = res.json()
            if data.get("auth"):
                st.session_state.logged_in = True
                st.session_state.username = data["username"]
                st.success("Доступ разрешен!")
                st.rerun()
            else:
                st.error("Неверный логин или пароль")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()  # Останавливаем выполнение остального кода

# --- Дальше идет твой обычный код главной страницы ---
st.sidebar.write(f"Вы вошли как: **{st.session_state.username}**")
if st.sidebar.button("Выйти"):
    del st.session_state.logged_in
    st.rerun()

st.set_page_config(page_title="MKS Manager", layout="wide")

st.title("🚀 Система управления электросетями")
st.markdown("""
Добро пожаловать в систему учета ТП.
Используйте боковое меню для навигации:
* **Просмотр базы**: поиск по ТП и просмотр абонентов.
* **Добавить новую ТП**: динамическое создание ТП, Лучей и Абонентов.
* **Экспорт**: выгрузка данных в Excel.
""")
