import streamlit as st
import requests
import streamlit as st
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
API_URL = "http://127.0.0.1:8000"
st.set_page_config(layout="wide")

st.title("📅 Заявки на создание ТП")

# --- ФОРМА СОЗДАНИЯ ЗАЯВКИ ---
with st.expander("➕ Создать новую заявку"):
    with st.form("task_form"):
        num = st.text_input("Номер ТП")
        dist = st.text_input("Район")
        exec_name = st.text_input("Исполнитель")
        date = st.date_input("Дата готовности")

        if st.form_submit_button("Добавить в план"):
            # ПРОВЕРКА: есть ли такая ТП уже в основной базе
            check_tp = requests.get(f"{API_URL}/tps/check-number/{num}").json()
            if check_tp.get("exists"):
                st.error("❌ Эта ТП уже создана в базе! Заявка не нужна.")
            else:
                payload = {
                    "tp_number": num,
                    "district": dist,
                    "executor": exec_name,
                    "deadline": str(date)}
                requests.post(f"{API_URL}/tasks/", json=payload)
                st.rerun()

# --- ОТРИСОВКА КАРТОЧЕК ---
# --- ОТРИСОВКА КАРТОЧЕК ---
res = requests.get(f"{API_URL}/tasks/")

if res.status_code == 200:
    tasks = res.json()

    # Проверяем, что нам пришел именно список, а не строка или ошибка
    if isinstance(tasks, list):
        if not tasks:
            st.info("📅 В плане пока нет активных заявок.")
        else:
            cols = st.columns(3)
            for idx, task in enumerate(tasks):
                # Дополнительная проверка, что task - это словарь
                if isinstance(task, dict):
                    with cols[idx % 3].container(border=True):
                        st.subheader(f"⚡ ТП {task.get('tp_number', '???')}")
                        st.write(f"📍 Район: **{task.get('district', '-')}**")
                        st.write(f"👤 Кто: **{task.get('executor', '-')}**")
                        st.write(f"📅 Срок: **{task.get('deadline', '-')}**")

                        if st.button(
                            "🏗️ Создать ТП",
                            key=f"go_{task.get('id', idx)}",
                                use_container_width=True):
                            st.session_state.prefill_tp = task
                            st.switch_page("pages/2_➕_Add_TP.py")
                            st.rerun()
    else:
        st.error(f"Ошибка данных: Ожидался список, получено: {type(tasks)}")
else:
    st.error(f"Не удалось получить список заявок. Код: {res.status_code}")
