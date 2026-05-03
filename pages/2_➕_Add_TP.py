import streamlit as st
import requests
import copy
import uuid
from ui_components import tp_fields, subscriber_fields, bus_fields, section_fields
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Добавить ТП", layout="wide")
st.title("➕ Добавление новой ТП")


# 1. Инициализация состояния
if "new_tp" not in st.session_state:
    st.session_state.new_tp = {"tp_number": "", "sections": []}
if "sub_buffer" not in st.session_state:
    st.session_state.sub_buffer = None
if "sub_salts" not in st.session_state:
    st.session_state.sub_salts = {}

if "prefill_tp" in st.session_state:
    p = st.session_state.prefill_tp
    st.session_state.new_tp["tp_number"] = p["tp_number"]
    st.session_state.new_tp["district"] = p["district"]
tp = st.session_state.new_tp
tp_number = st.text_input(
    "📝 Номер ТП",
    value=tp.get(
        "tp_number",
        ""),
    placeholder="Напр: ТП-500")
if tp_number:
    try:
        check_res = requests.get(f"{API_URL}/tps/check-number/{tp_number}")
        if check_res.status_code == 200 and check_res.json().get("exists"):
            st.error(
                f"⚠️ Внимание! ТП №{tp_number} уже зарегистрирована в системе.")
            st.stop()  # Здесь выполнение прервется, форма ниже не появится
        else:
            tp["tp_number"] = tp_number
    except BaseException:
        pass

if st.button("➕ Добавить новый Луч"):
    tp["sections"].append(
        {"number": f"Луч {len(tp['sections'])+1}", "subscribers": []})
    st.rerun()

with st.form("add_tp_form"):
    tp["tp_number"] = st.text_input("📝 Номер ТП", value=tp["tp_number"])
    tp.update(tp_fields(tp))

    for s_idx, sec in enumerate(tp["sections"]):
        st.divider()
        with st.expander(f"📍 {sec['number']}", expanded=True):
            sec.update(section_fields(sec, key_prefix=f"s_{s_idx}"))

            for a_idx, sub in enumerate(sec["subscribers"]):
                with st.container(border=True):
                    sub_id = f"{s_idx}_{a_idx}"
                    if sub_id not in st.session_state.sub_salts:
                        st.session_state.sub_salts[sub_id] = str(uuid.uuid4())[
                            :8]

                    salt = st.session_state.sub_salts[sub_id]

                    c_h, c_cp, c_ps, c_dl = st.columns([0.4, 0.2, 0.2, 0.1])
                    c_h.write(f"👤 **Абонент №{a_idx + 1}**")

                    # Логика кнопок управления
                    if c_cp.form_submit_button(
                            "📋 Копировать", key=f"cp_{sub_id}_{salt}"):
                        st.session_state.sub_buffer = copy.deepcopy(sub)
                        st.toast("Данные скопированы")

                    if c_ps.form_submit_button(
                            "📥 Вставить", key=f"ps_{sub_id}_{salt}"):
                        if st.session_state.sub_buffer:
                            # Вставляем полную копию
                            st.session_state.new_tp["sections"][s_idx][
                                "subscribers"][a_idx] = copy.deepcopy(
                                st.session_state.sub_buffer)
                            # Меняем соль для обновления экрана
                            st.session_state.sub_salts[sub_id] = str(uuid.uuid4())[
                                :8]
                            st.rerun()
                        else:
                            st.warning("Буфер пуст!")

                    if c_dl.form_submit_button(
                            "🗑️", key=f"dl_{sub_id}_{salt}"):
                        sec["subscribers"].pop(a_idx)
                        st.rerun()

                    # --- ОТРИСОВКА (Всегда идет после логики кнопок) ---
                    # Поля абонента
                    sub.update(
                        subscriber_fields(
                            sub, key_prefix=f"sub_{sub_id}_{salt}"))

                    # Шины абонента
                    st.write("🔗 **Шины**")
                    for b_idx, bus in enumerate(sub.get("buses", [])):
                        # Каждая шина получает уникальный ключ через UUID для
                        # стабильности
                        if "_uuid" not in bus:
                            bus["_uuid"] = str(uuid.uuid4())

                        bus_fields(
                            bus, key_prefix=f"bus_{bus['_uuid']}_{salt}")

                    if st.form_submit_button(
                            "➕ Добавить шину", key=f"add_bus_{sub_id}_{salt}"):
                        sub.setdefault(
                            "buses", []).append(
                            {"bus_type": "", "bus_count": 1,
                             "_uuid": str(uuid.uuid4())})
                        st.rerun()

            if st.form_submit_button(
                "👤 Добавить абонента",
                    key=f"as_btn_{s_idx}"):
                sec["subscribers"].append(
                    {"name": "", "number": "", "buses": []})
                st.rerun()

    # --- ЭТОТ БЛОК ДОЛЖЕН БЫТЬ ВНУТРИ with st.form ---
    st.divider()
    sc1, sc2 = st.columns(2)

    if sc1.form_submit_button("💾 СОХРАНИТЬ ТП", use_container_width=True):
        if not tp["tp_number"]:
            st.error("❌ Ошибка: Введите номер ТП!")
        else:
            payload = copy.deepcopy(st.session_state.new_tp)

            # Функция очистки от технических полей
            def clean_for_api(node):
                if isinstance(node, dict):
                    keys_to_del = [k for k in node.keys() if k.startswith("_")]
                    for k in keys_to_del:
                        del node[k]
                    for v in node.values():
                        clean_for_api(v)
                elif isinstance(node, list):
                    for item in node:
                        clean_for_api(item)

            clean_for_api(payload)

            try:
                res = requests.post(f"{API_URL}/tps/", json=payload)

                if res.status_code == 200:
                    if "prefill_tp" in st.session_state:
                        task_id = st.session_state.prefill_tp["id"]
                        requests.delete(f"{API_URL}/tasks/{task_id}")
                        del st.session_state.prefill_tp
                    st.success(f"✅ ТП {tp['tp_number']} успешно сохранена!")
                    st.session_state.new_tp = {"tp_number": "", "sections": []}
                    st.switch_page("pages/1_📋_View_TP.py")

                elif res.status_code == 400:
                    # Выводим именно то сообщение, которое прислал Бэкенд
                    error_msg = res.json().get("detail", "Ошибка валидации")
                    st.error(f"🚫 {error_msg}")
                else:
                    st.error("❌ Непредвиденная ошибка при сохранении")

            except Exception as e:
                st.error(f"📡 Ошибка связи с сервером: {e}")

    if sc2.form_submit_button("🧹 ОЧИСТИТЬ ФОРМУ", use_container_width=True):
        st.session_state.new_tp = {"tp_number": "", "sections": []}
        st.session_state.sub_salts = {}
        st.rerun()
