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
                    st.session_state.role = data.get("role") 
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
            except Exception as e:
                st.error(f"Ошибка связи с сервером: {e}")

# --- Определение страниц ---
# Страница для неавторизованных
login_screen = st.Page(login_page, title="Вход", icon="🔒")




# --- Определение страниц ---
# Базовые страницы, доступные всем сотрудникам
common_pages = [
    st.Page("pages/1_View_TP.py", title="Просмотр ТП", icon="💻"),
    st.Page("pages/3_Tasks.py", title="Заявки", icon="📝"),
]

# Отдельная страница для админа
admin_page = [
    st.Page("pages/2_Add_TP.py", title="Добавить новую ТП", icon="➕"),
    st.Page("pages/4_Settings.py", title="Настройки", icon="⚙️"),
    st.Page("pages/5_Visio_Viewer.py", title="Просмотр карты НН", icon="🗺️"),
    st.Page("pages/6_Export.py", title="Экспорт в xlsx", icon="📊"),
    st.Page("pages/7_Admin.py", title="Администрирование", icon="🔐"),
]

# --- Логика навигации ---
if st.session_state.logged_in:
    # 1. Формируем список страниц в зависимости от роли
    pages_to_show = common_pages.copy()
    
    if st.session_state.role == "admin":
        pages_to_show.extend(admin_page)
    
    # 2. Оформляем сайдбар
    st.sidebar.write(f"👤: **{st.session_state.username}** (`{st.session_state.role}`)")
    if st.sidebar.button("Выйти", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()
    
    # 3. Запускаем навигацию по отфильтрованному списку
    pg = st.navigation({"Основное меню": pages_to_show})
else:
    # Если не вошли — доступна только страница логина
    pg = st.navigation([login_screen])





# Запускаем выбранную страницу
pg.run()
