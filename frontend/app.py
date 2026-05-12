import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# 1. Настройка страницы (обязательно первая команда)
st.set_page_config(page_title="MKS Manager", layout="wide")

# 2. Инициализация менеджера куки
# Пароль нужен для шифрования данных в браузере
cookies = EncryptedCookieManager(password="secret_password_for_cookies_123")
if not cookies.ready():
    st.stop()

API_URL = "http://127.0.0.1:8000"

# --- 3. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
# Создаем ключи заранее, чтобы код не падал при обращении к ним
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nickname = None
    st.session_state.role = None
    st.session_state.access_token = None

# Восстановление сессии из куки при обновлении (F5)
if not st.session_state.logged_in:
    token = cookies.get("access_token")
    if token:
        st.session_state.logged_in = True
        st.session_state.access_token = token
        st.session_state.username = cookies.get("mks_user")
        st.session_state.nickname = cookies.get("mks_nick")
        st.session_state.role = cookies.get("mks_role")
        st.rerun()

# --- 4. ФУНКЦИИ УПРАВЛЕНИЯ ---


def login_page():
    st.title("🔐 Вход в систему")
    with st.form("login_form"):
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти", use_container_width=True):
            try:
                res = requests.post(
                    f"{API_URL}/auth/login", data={"username": u, "password": p}
                )
                if res.status_code == 200:
                    data = res.json()
                    # Сохраняем в сессию
                    st.session_state.logged_in = True
                    st.session_state.access_token = data["access_token"]
                    st.session_state.username = data["username"]
                    st.session_state.nickname = data.get("nickname")
                    st.session_state.role = data.get("role")

                    # Сохраняем в куки (чтобы JWT не пропадал)
                    cookies["access_token"] = data["access_token"]
                    cookies["mks_user"] = data["username"]
                    cookies["mks_nick"] = data.get("nickname")
                    cookies["mks_role"] = data.get("role")
                    cookies.save()

                    st.rerun()
                else:
                    st.error("❌ Неверный логин или пароль")
            except Exception as e:
                st.error(f"🔌 Ошибка связи: {e}")


def logout():
    # Очищаем куки
    for key in ["access_token", "mks_user", "mks_role"]:
        if key in cookies:
            del cookies[key]
    cookies.save()

    # Сбрасываем сессию
    st.session_state.logged_in = False
    st.session_state.access_token = None
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()


# --- 5. ОПРЕДЕЛЕНИЕ СТРАНИЦ ---

login_screen = st.Page(login_page, title="Вход", icon="🔒")

common_pages = [
    st.Page("pages/1_View_TP.py", title="Просмотр ТП", icon="💻"),
    st.Page("pages/3_Tasks.py", title="Заявки", icon="📝"),
]

admin_pages = [
    st.Page("pages/2_Add_TP.py", title="Добавить новую ТП", icon="➕"),
    st.Page("pages/4_Settings.py", title="Настройки", icon="⚙️"),
    st.Page("pages/5_Visio_Viewer.py", title="Просмотр карты НН", icon="🗺️"),
    st.Page("pages/6_Export.py", title="Экспорт в xlsx", icon="📊"),
    st.Page("pages/7_Admin.py", title="Администрирование", icon="🔐"),
]

# --- 6. НАВИГАЦИЯ ---

if st.session_state.logged_in:
    pages_to_show = common_pages.copy()

    # Безопасно проверяем роль админа
    if st.session_state.role == "admin":
        pages_to_show.extend(admin_pages)

    # Отображение юзера в сайдбаре
    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    st.sidebar.caption(f"Доступ: {st.session_state.role}")

    if st.sidebar.button("Выйти", use_container_width=True, key="logout_sidebar"):
        logout()

    pg = st.navigation({"Меню": pages_to_show})
else:
    pg = st.navigation([login_screen])

pg.run()
