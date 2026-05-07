from datetime import datetime, timedelta

import requests
import streamlit as st

# 1. ПРОВЕРКА АВТОРИЗАЦИИ
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

API_URL = "http://127.0.0.1:8000"
curr_user = st.session_state.get("username")
is_admin = st.session_state.get("role") == "admin"

st.title("📅 Заявки на создание ТП")
tomorrow = datetime.now() + timedelta(days=1)

# 2. ФУНКЦИЯ ОЧИСТКИ
def reset_task_form():
    st.session_state["f_num"] = ""
    st.session_state["f_dist"] = ""
    st.session_state["f_ppo"] = ""
    st.session_state["f_comm"] = ""

# 3. СБРОС ДО ОТРИСОВКИ ФОРМЫ (решение ошибки StreamlitAPIException)
if st.session_state.get("needs_reset"):
    reset_task_form()
    st.session_state["needs_reset"] = False

# Инициализация ключей
for key in ["f_num", "f_dist", "f_ppo", "f_comm"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- 4. ФОРМА СОЗДАНИЯ ЗАЯВКИ ---
with st.expander("➕ Создать новую заявку"):
    with st.form("new_task"):
        num = st.text_input("Номер ТП", key="f_num", placeholder="Только цифры")
        dist = st.text_input("Район", key="f_dist", placeholder="Только цифры")
        deadline = st.date_input("Дедлайн", value=tomorrow)
        
        if is_admin:
            exec_name_input = st.text_input("Исполнитель", value=curr_user)
        else:
            exec_name_input = curr_user
        
        ppo = st.text_input("Ссылка на ППО (Яндекс.Диск)", key="f_ppo", placeholder="https://yandex.ru...")
        comm = st.text_area("Комментарий", key="f_comm")
        
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            clear_clicked = st.form_submit_button("🧹 Очистить")
        with col_btn2:
            submit = st.form_submit_button("Добавить в план", use_container_width=True)

    # ОБРАБОТКА ФОРМЫ
    if clear_clicked:
        st.session_state["needs_reset"] = True
        st.rerun()

    if submit:
        num_clean = num.strip()
        dist_clean = dist.strip()

        if not num_clean or not dist_clean:
            st.error("❌ Ошибка: Номер ТП и Район обязательны!")
        elif not num_clean.isdigit() or not dist_clean.isdigit():
            st.error("❌ В полях ТП и Район допускаются только цифры!")
        else:
            try:
                res_tp = requests.get(f"{API_URL}/tps/check-number/{num_clean}").json()
                res_task = requests.get(f"{API_URL}/tasks/check-exists/{num_clean}").json()

                if res_tp.get("exists"):
                    st.error(f"❌ ТП {num_clean} уже внесена в основную базу!")
                elif res_task.get("exists"):
                    st.error(f"⚠️ Заявка на ТП {num_clean} уже есть в плане!")
                else:
                    payload = {
                        "tp_number": num_clean,
                        "district": dist_clean,
                        "executor": exec_name_input,
                        "deadline": str(deadline),
                        "comment": comm,
                        "ppo_report": ppo
                    }
                    post_res = requests.post(f"{API_URL}/tasks/", json=payload)
                    if post_res.status_code in [200, 201]:
                        st.success("✅ Заявка создана")
                        st.session_state["needs_reset"] = True
                        st.rerun()
                    else:
                        st.error(f"Ошибка сервера: {post_res.text}")
            except Exception as e:
                st.error(f"🔌 Ошибка связи: {e}")

# --- 5. СПИСОК КАРТОЧЕК ---
res = requests.get(f"{API_URL}/tasks/")
if res.status_code == 200:
    all_tasks = res.json()
    display_tasks = all_tasks if is_admin else [t for t in all_tasks if t.get("executor") == curr_user]

    if not display_tasks:
        st.info("Нет активных заявок.")
    else:
        cols = st.columns(3)
        for idx, task in enumerate(display_tasks):
            with cols[idx % 3].container(border=True):
                st.subheader(f"⚡ ТП {task.get('tp_number')}")
                st.write(f"📍 Район: **{task.get('district')}**")
                
                # Отображение ссылки ППО
                ppo_link = task.get('ppo_report', '').strip()
                if ppo_link.startswith("http"):
                    st.link_button("📂 Открыть ППО", ppo_link, use_container_width=True)
                else:
                    st.write(f"📝 ППО: {ppo_link if ppo_link else '-'}")

                if is_admin:
                    st.caption(f"👤 {task.get('executor')} | 📅 {task.get('deadline')}")
                    if st.button("🏗️ Создать ТП", key=f"build_{task['id']}", use_container_width=True):
                        st.session_state.prefill_tp = task
                        st.switch_page("pages/2_Add_TP.py")

                # Управление
                e_col, d_col = st.columns(2)
                with e_col:
                    with st.popover("📝", use_container_width=True):
                        st.write("### Редактирование")
                        n_dist = st.text_input("Район", value=task.get("district"), key=f"ed_d_{task['id']}")
                        n_ppo = st.text_input("Ссылка ППО", value=task.get("ppo_report"), key=f"ed_p_{task['id']}")
                        n_comm = st.text_area("Комментарий", value=task.get("comment"), key=f"ed_c_{task['id']}")
                        
                        if st.button("Обновить", key=f"save_{task['id']}", use_container_width=True):
                            upd = {"district": n_dist, "ppo_report": n_ppo, "comment": n_comm}
                            requests.patch(f"{API_URL}/tasks/{task['id']}", json=upd)
                            st.rerun()
                
                with d_col:
                    if st.button("🗑️", key=f"del_{task['id']}", use_container_width=True):
                        requests.delete(f"{API_URL}/tasks/{task['id']}")
                        st.rerun()

                if task.get("comment"):
                    with st.expander("💬"):
                        st.write(task['comment'])
