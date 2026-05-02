import streamlit as st
import requests
from datetime import date

API_URL = "http://127.0.0.1:8000"

st.title("➕ Регистрация новой ТП")

# Инициализация состояния формы в session_state
if "form_data" not in st.session_state:
    st.session_state.form_data = {"sections": []}

# --- БЛОК 1: ОСНОВНЫЕ ДАННЫЕ ТП ---
with st.expander("основные характеристики ТП", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        tp_number = st.text_input("Номер ТП*", placeholder="Например: ТП-500")
        district = st.text_input("Район")
        region = st.text_input("Округ")
    with col2:
        address = st.text_input("Адрес ТП")
        voltage = st.selectbox(
            "Напряжение", [
                "10/0.4 кВ", "6/0.4 кВ", "20/0.4 кВ", "0.4 кВ"])
        exec_type = st.text_input(
            "Тип исполнения",
            placeholder="БКТП, Киосковая...")
    with col3:
        trans_type = st.text_input("Тип трансформатора")
        uspd_type = st.text_input("Тип УСПД")
        comm_date = st.date_input("Дата включения", value=date.today())

st.divider()

# --- БЛОК 2: УПРАВЛЕНИЕ СТРУКТУРОЙ (ЛУЧИ И АБОНЕНТЫ) ---
st.subheader("Структура секций (лучей)")

if st.button("➕ Добавить новый Луч"):
    st.session_state.form_data["sections"].append({
        "number": "",
        "assembly_type": "",
        "panel": "",
        "subscribers": []
    })

# Отрисовка каждой секции
for s_idx, sec in enumerate(st.session_state.form_data["sections"]):
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        sec["number"] = c1.text_input(
            "Название луча",
            key=f"s_n_{s_idx}",
            placeholder="Луч А")
        sec["assembly_type"] = c2.text_input("Тип сборки", key=f"s_at_{s_idx}")
        sec["panel"] = c3.text_input("Панель", key=f"s_p_{s_idx}")

        if c4.button("🗑️", key=f"del_s_{s_idx}", help="Удалить луч"):
            st.session_state.form_data["sections"].pop(s_idx)
            st.rerun()

        # Добавление абонента в луч
        if st.button(
            f"👤 Добавить абонента в {sec['number'] if sec['number'] else 'этот луч'}",
                key=f"add_sub_{s_idx}"):
            sec["subscribers"].append({
                "number": "", "name": "", "address": "", "fuse_rating": "",
                "cable_brand": "", "cable_length": 0.0, "ct_rating": "",
                "ct_type": "", "meter_type": "", "buses": []
            })

        # Список абонентов внутри луча
        for a_idx, sub in enumerate(sec["subscribers"]):
            with st.expander(f"Абонент: {sub['name'] if sub['name'] else 'Новый'}"):
                row1_col1, row1_col2, row1_col3 = st.columns(3)
                sub["number"] = row1_col1.text_input(
                    "№ Абонента", key=f"a_num_{s_idx}_{a_idx}")
                sub["name"] = row1_col2.text_input(
                    "Наименование", key=f"a_nam_{s_idx}_{a_idx}")
                sub["address"] = row1_col3.text_input(
                    "Адрес", key=f"a_adr_{s_idx}_{a_idx}")

                row2_col1, row2_col2, row2_col3 = st.columns(3)
                sub["fuse_rating"] = row2_col1.text_input(
                    "Предохранитель", key=f"a_fs_{s_idx}_{a_idx}")
                sub["cable_brand"] = row2_col2.text_input(
                    "Марка кабеля", key=f"a_cb_{s_idx}_{a_idx}")
                sub["cable_length"] = row2_col3.number_input(
                    "Длина кабеля (м)", key=f"a_cl_{s_idx}_{a_idx}", min_value=0.0)

                row3_col1, row3_col2, row3_col3 = st.columns(3)
                sub["ct_rating"] = row3_col1.text_input(
                    "Номинал ТТ", key=f"a_ctr_{s_idx}_{a_idx}")
                sub["ct_type"] = row3_col2.text_input(
                    "Тип ТТ", key=f"a_ctt_{s_idx}_{a_idx}")
                sub["meter_type"] = row3_col3.text_input(
                    "Тип ПУ", key=f"a_mt_{s_idx}_{a_idx}")

                # --- ВНУТРЕННИЙ БЛОК ШИН ---
                st.markdown("#### 🔗 Шины абонента")

                # Кнопка добавления новой шины именно этому абоненту
                if st.button(
                    f"➕ Добавить шину",
                        key=f"add_bus_{s_idx}_{a_idx}"):
                    sub["buses"].append({"bus_type": "", "bus_count": 1})
                    st.rerun()

                # Список шин
                for b_idx, bus in enumerate(sub["buses"]):
                    bc1, bc2, bc3 = st.columns([3, 2, 1])
                    bus["bus_type"] = bc1.text_input(
                        "Тип шины",
                        key=f"b_t_{s_idx}_{a_idx}_{b_idx}",
                        placeholder="Медная 40х4"
                    )
                    bus["bus_count"] = bc2.number_input(
                        "Кол-во",
                        key=f"b_c_{s_idx}_{a_idx}_{b_idx}",
                        min_value=1,
                        step=1
                    )
                    if bc3.button("❌", key=f"del_b_{s_idx}_{a_idx}_{b_idx}"):
                        sub["buses"].pop(b_idx)
                        st.rerun()

                if st.button(
                    "🗑️ Удалить абонента",
                        key=f"del_a_{s_idx}_{a_idx}"):
                    sec["subscribers"].pop(a_idx)
                    st.rerun()

st.divider()

# --- КНОПКА СОХРАНЕНИЯ ---
if st.button(
    "💾 СОХРАНИТЬ ВСЮ ТП В БАЗУ",
    type="primary",
        use_container_width=True):
    if not tp_number:
        st.error("Ошибка: Поле 'Номер ТП' должно быть заполнено!")
    else:
        full_payload = {
            "tp_number": tp_number,
            "district": district,
            "region": region,
            "address": address,
            "voltage": voltage,
            "execution_type": exec_type,
            "transformer_type": trans_type,
            "uspd_type": uspd_type,
            "commissioning_date": str(comm_date),
            "sections": st.session_state.form_data["sections"]
        }

        try:
            response = requests.post(f"{API_URL}/tps/", json=full_payload)
            if response.status_code == 200:
                st.success(
                    f"✅ ТП {tp_number} со всей структурой успешно сохранена!")
                st.session_state.form_data = {"sections": []}  # Очистка формы
                st.balloons()
            else:
                st.error(f"Ошибка API: {response.text}")
        except Exception as e:
            st.error(f"Не удалось связаться с сервером: {e}")
