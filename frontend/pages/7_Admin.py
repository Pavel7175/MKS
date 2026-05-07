import requests
import streamlit as st

# 1. Защита страницы
if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("⛔ Доступ только для администраторов")
    st.stop()

API_URL = "http://127.0.0.1:8000"

st.title("🔐 Управление пользователями")

# --- СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ ---
with st.expander("👤 Зарегистрировать нового сотрудника"):
    with st.form("admin_create_user", clear_on_submit=True):
        new_login = st.text_input("Логин (ФИО или Табельный)")
        new_pass = st.text_input("Пароль", type="password")
        new_role = st.selectbox("Роль доступа", ["user", "admin"])
        
        if st.form_submit_button("Создать аккаунт"):
                                            
            if new_login and new_pass:
                res = requests.post(
                    f"{API_URL}/auth/users/create",
                    params={
                        "username": new_login, 
                        "password": new_pass,
                        "current_admin": st.session_state.username # Передаем имя админа из сессии
                    }
                )       
                # Создаем пользователя
                # res = requests.post(
                #     f"{API_URL}/auth/users/create", 
                #     params={"username": new_login, "password": new_pass}
                # )
                if res.status_code == 200:
                    created_user = res.json()
                    # Если выбрали admin, обновляем роль (т.к. дефолт "user")
                    if new_role == "admin":
                        requests.patch(
                            f"{API_URL}/auth/users/{created_user['id']}/role", 
                            params={"new_role": "admin"}
                        )
                    st.success(f"✅ Пользователь {new_login} создан")
                    st.rerun()
                else:
                    st.error(f"Ошибка: {res.json().get('detail')}")

st.divider()

# --- СПИСОК И УДАЛЕНИЕ ---
st.subheader("👥 Список учетных записей")
res = requests.get(f"{API_URL}/auth/users")

if res.status_code == 200:
    users = res.json()
    for user in users:
        # Не показываем текущего админа в списке на удаление самого себя
        is_me = user['username'] == st.session_state.get("username")
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"🆔 {user['id']} | **{user['username']}**")
            with col2:
                st.code(user['role'])
            with col3:
                if not is_me:
                    if st.button("🗑️ Удалить", key=f"del_{user['id']}", use_container_width=True):
                        requests.delete(f"{API_URL}/auth/users/{user['id']}")
                        st.rerun()
                else:
                    st.caption("Это вы")
