import requests
import streamlit as st

# 1. ЭТО ДОЛЖНО БЫТЬ ПЕРВОЙ КОМАНДОЙ STREAMLIT
st.set_page_config(page_title="MKS Manager", layout="wide")

API_URL = "http://127.0.0.1:8000"

# --- Инициализация состояния ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Функция входа ---
def login_page():
    st.title("🔐 Вход в систему МКС")
    with st.form("login_form"):
        user = st.text_input("Логин")
        pw = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            try:
                res = requests.post(
                    f"{API_URL}/auth/login",
                    params={"username": user, "password": pw}
                )
                data = res.json()
                if data.get("auth"):
                    st.session_state.logged_in = True
                    st.session_state.username = data["username"]
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
            except Exception as e:
                st.error(f"Ошибка связи с сервером: {e}")

# --- Определение страниц ---
# Страница для неавторизованных
login_screen = st.Page(login_page, title="Вход", icon="🔒")

# Основное меню (только для авторизованных)
user_pages = [
    st.Page("pages/1_View_TP.py", title="Просмотр ТП", icon="💻"),
    st.Page("pages/2_Add_TP.py", title="Добавить новую ТП", icon="➕"),
    st.Page("pages/3_Tasks.py", title="Заявки", icon="📝"),
    st.Page("pages/4_Settings.py", title="Настройки", icon="⚙️"),
    st.Page("pages/5_Visio_Viewer.py", title="Просмотр карты НН", icon="🗺️"),
    st.Page("pages/6_Export.py", title="Экспорт в xlsx", icon="📊"),
]

# --- Логика навигации ---
if st.session_state.logged_in:
    # Если вошли — показываем меню и кнопку выхода в сайдбаре
    st.sidebar.write(f"👤: **{st.session_state.username}**")
    if st.sidebar.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    pg = st.navigation({"Меню": user_pages})
else:
    # Если не вошли — доступна только страница логина
    pg = st.navigation([login_screen])

# Запускаем выбранную страницу
pg.run()
