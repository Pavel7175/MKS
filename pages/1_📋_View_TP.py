import streamlit as st
import requests
import pandas as pd
from ui_components import tp_fields, subscriber_fields  # Тот самый вынос полей

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Реестр ТП", layout="wide")
st.title("📋 Реестр и управление ТП")

# Инициализация хранилища для редактирования
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "edit_data" not in st.session_state:
    st.session_state.edit_data = {}

search_query = st.text_input("🔍 Поиск по номеру ТП (напр. ТП-500)")
url = f"{API_URL}/tps/by-number/{search_query}" if search_query else f"{API_URL}/tps/"

try:
    res = requests.get(url)
    tps = []
    if res.status_code == 200:
        data = res.json()
        tps = [data] if isinstance(data, dict) else data
except BaseException:
    st.error("Нет связи с сервером API")
    tps = []
for tp in tps:
    is_editing = st.session_state.edit_mode == tp['id']

    with st.expander(f"🏢 {tp['tp_number']} — {tp['address']}", expanded=is_editing):
        if not is_editing:
            # Основные данные ТП
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Район/Округ:** {tp['district']} / {tp['region']}")
            c1.write(f"**Напряжение:** {tp['voltage']}")
            c2.write(f"**Трансформатор:** {tp['transformer_type']}")
            c2.write(f"**Исполнение:** {tp['execution_type']}")
            c3.write(f"**УСПД:** {tp['uspd_type']}")
            c3.write(f"**Дата вкл:** {tp['commissioning_date']}")

            if st.button(
                "📝 Редактировать ТП и структуру",
                    key=f"btn_ed_{tp['id']}"):
                st.session_state.edit_mode = tp['id']
                st.session_state.edit_data = tp.copy()
                st.rerun()

            # Детальный просмотр абонентов
            for sec in tp['sections']:
                st.markdown(
                    f"#### 📍 Луч: {sec['number']} (Панель: {sec['panel']})")
                for sub in sec['subscribers']:
                    with st.container(border=True):
                        st.write(
                            f"👤 **{sub['name']}** (№{sub['number']}) | 🏠 {sub['address']}")
                        sa1, sa2, sa3 = st.columns(3)
                        sa1.write(
                            f"**Кабель:** {sub['cable_brand']} ({sub['cable_length']}м)")
                        sa1.write(f"**Предохранитель:** {sub['fuse_rating']}")
                        sa2.write(
                            f"**ТТ:** {sub['ct_type']} ({sub['ct_rating']})")
                        sa3.write(f"**ПУ:** {sub['meter_type']}")

                        if sub.get('buses'):
                            st.caption("🔗 Шины:")
                            st.table(pd.DataFrame(sub['buses'])[
                                     ['bus_type', 'bus_count']])
        else:
            # --- РЕЖИМ ПОЛНОГО РЕДАКТИРОВАНИЯ ---
            st.warning(f"🛠 Редактирование структуры ТП: {tp['tp_number']}")
            ed = st.session_state.edit_data

            # 1. Кнопки управления структурой (вне формы для мгновенного
            # обновления)
            c_add1, c_add2 = st.columns(2)
            if c_add1.button(
                "➕ Добавить новый Луч",
                    key=f"add_sec_{tp['id']}"):
                ed['sections'].append(
                    {"number": "Новый луч", "assembly_type": "", "panel": "",
                     "subscribers": []})
                st.rerun()

            # 2. Сама форма для ввода данных
            with st.form(f"f_edit_{tp['id']}"):
                ed = tp_fields(ed)  # Общие поля ТП из ui_components

                for s_idx, sec in enumerate(ed['sections']):
                    st.divider()
                    col_sec_h, col_sec_del = st.columns([0.9, 0.1])
                    col_sec_h.subheader(f"Луч: {sec['number']}")

                    # Удаление луча
                    if col_sec_del.form_submit_button(
                            "🗑️", help="Удалить луч"):
                        ed['sections'].pop(s_idx)
                        st.rerun()

                    col_s1, col_s2 = st.columns(2)
                    sec['number'] = col_s1.text_input(
                        "Название луча", value=sec['number'], key=f"e_sn_{s_idx}")
                    sec['panel'] = col_s2.text_input(
                        "Панель", value=sec['panel'], key=f"e_sp_{s_idx}")

                    # Кнопка добавления абонента (внутри формы это должен быть submit, либо делаем костыль)
                    # В Streamlit кнопка внутри формы не может менять состояние без сабмита,
                    # поэтому используем checkbox или выносим кнопку из формы.
                    # Оптимально: оставить кнопки добавления абонентов ВНЕ
                    # формы для удобства.

                    for a_idx, sub in enumerate(sec['subscribers']):
                        with st.container(border=True):
                            col_sub_h, col_sub_del = st.columns([0.9, 0.1])
                            col_sub_h.write(
                                f"**Абонент: {sub['name'] if sub['name'] else 'Новый'}**")
                            if col_sub_del.form_submit_button(
                                    "❌", help="Удалить абонента"):
                                sec['subscribers'].pop(a_idx)
                                st.rerun()

                            sub = subscriber_fields(
                                sub, key_prefix=f"e_sub_{s_idx}_{a_idx}")

                # Кнопки сохранения/отмены
                bc1, bc2 = st.columns(2)
                if bc1.form_submit_button(
                        "✅ СОХРАНИТЬ ВСЁ", use_container_width=True):
                    res = requests.patch(f"{API_URL}/tps/{tp['id']}", json=ed)
                    if res.status_code == 200:
                        st.success("Данные в базе обновлены!")
                        st.session_state.edit_mode = None
                        st.rerun()

                if bc2.form_submit_button(
                        "❌ ОТМЕНА", use_container_width=True):
                    st.session_state.edit_mode = None
                    st.rerun()

            # 3. Кнопки добавления абонентов (вынесены под форму для корректной
            # работы)
            for s_idx, sec in enumerate(ed['sections']):
                if st.button(
                    f"👤 Добавить абонента в {sec['number']}",
                        key=f"add_sub_btn_{s_idx}"):
                    sec['subscribers'].append({
                        "number": "", "name": "", "address": "", "fuse_rating": "",
                        "cable_brand": "", "cable_length": 0.0, "ct_rating": "",
                        "ct_type": "", "meter_type": "", "buses": []
                    })
                    st.rerun()
