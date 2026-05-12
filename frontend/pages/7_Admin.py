import requests
import streamlit as st

# 1. Защита страницы
if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("⛔ Доступ только для администраторов")
    st.stop()

API_URL = "http://127.0.0.1:8000"

# 2. ПОДГОТОВКА ТОКЕНА
token = st.session_state.get("access_token")
headers = {"Authorization": f"Bearer {token}"}

st.title("🔐 Управление пользователями")

# --- 3. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ ---
with st.expander("👤 Зарегистрировать нового сотрудника"):
    with st.form("admin_create_user", clear_on_submit=True):
        new_login = st.text_input("Логин (для входа)")
        new_nick = st.text_input("Имя сотрудника (Никнейм)")
        new_pass = st.text_input("Пароль", type="password")
        new_role = st.selectbox("Роль доступа", ["user", "admin"])

        if st.form_submit_button("Создать аккаунт", use_container_width=True):
            if new_login and new_pass:
                # Если никнейм не ввели, используем логин
                display_name = new_nick if new_nick else new_login

                res = requests.post(
                    f"{API_URL}/auth/users/create",
                    params={
                        "username": new_login,
                        "password": new_pass,
                        "role": new_role,
                        "nickname": display_name,
                        "current_admin": st.session_state.username,
                    },
                    headers=headers,
                )

                if res.status_code == 200:
                    st.success(f"✅ Пользователь {display_name} создан")
                    st.rerun()
                else:
                    st.error(f"Ошибка {res.status_code}: {res.text}")

st.divider()

# --- 4. СПИСОК И УДАЛЕНИЕ ---
st.subheader("👥 Список учетных записей")

try:
    res = requests.get(f"{API_URL}/auth/users", headers=headers)

    if res.status_code == 200:
        users = res.json()

        if not users:
            st.info("Список пользователей пуст.")
        else:
            # Шапка таблицы
            h_col1, h_col2, h_col3, h_col4 = st.columns([1, 2, 2, 1])
            h_col1.caption("ID")
            h_col2.caption("Логин")
            h_col3.caption("Никнейм / Имя")
            h_col4.caption("Роль")

            for user in users:
                u_id = user.get("id")
                u_name = user.get("username", "—")
                u_nick = user.get("nickname", "—")  # ВЫВОД НИКНЕЙМА
                u_role = user.get("role", "—")

                is_me = u_name == st.session_state.get("username")

                with st.container(border=True):
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])

                    with col1:
                        st.write(f"`{u_id}`")
                    with col2:
                        st.write(f"**{u_name}**")
                    with col3:
                        st.write(u_nick)  # Здесь теперь отображается никнейм
                    with col4:
                        st.code(u_role)
                    with col5:
                        if not is_me:
                            if st.button(
                                "🗑️", key=f"del_{u_id}", use_container_width=True
                            ):
                                if (
                                    requests.delete(
                                        f"{API_URL}/auth/users/{u_id}", headers=headers
                                    ).status_code
                                    == 200
                                ):
                                    st.rerun()
                        else:
                            st.write("✅")

    elif res.status_code == 401:
        st.error("🔑 Сессия истекла. Перезайдите.")
    else:
        st.error(f"Ошибка сервера: {res.status_code}")
except Exception as e:
    st.error(f"🔌 Ошибка связи: {e}")
