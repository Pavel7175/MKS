import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Реестр ТП", layout="wide")
st.title("📋 Реестр и управление ТП")

# Инициализация состояния
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None  # ID редактируемой ТП
if "edit_data" not in st.session_state:
    st.session_state.edit_data = {}    # Буфер для правок

search_query = st.text_input("🔍 Поиск по номеру ТП (например: ТП-500)")
url = f"{API_URL}/tps/by-number/{search_query}" if search_query else f"{API_URL}/tps/"

try:
    res = requests.get(url)
    tps = []
    if res.status_code == 200:
        data = res.json()
        tps = [data] if isinstance(data, dict) else data
except BaseException:
    st.error("Ошибка связи с API")
    tps = []
for tp in tps:
    is_editing = st.session_state.edit_mode == tp['id']

    with st.expander(f"🏢 {tp['tp_number']} — {tp['address']}", expanded=is_editing or bool(search_query)):
        if not is_editing:
            # --- ВИД ПРОСМОТРА ---
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Район/Округ:** {tp['district']} / {tp['region']}")
            c1.write(f"**Напряжение:** {tp['voltage']}")
            c2.write(f"**Трансформатор:** {tp['transformer_type']}")
            c2.write(f"**Исполнение:** {tp['execution_type']}")
            c3.write(f"**УСПД:** {tp['uspd_type']}")
            c3.write(f"**Дата вкл:** {tp['commissioning_date']}")

            if st.button(f"📝 Редактировать всё", key=f"btn_ed_{tp['id']}"):
                st.session_state.edit_mode = tp['id']
                st.session_state.edit_data = tp.copy()
                st.rerun()

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
            st.warning(f"🛠 Правка структуры ТП: {tp['tp_number']}")
            ed = st.session_state.edit_data

            with st.form(f"full_edit_{tp['id']}"):
                # Поля самой ТП
                ec1, ec2 = st.columns(2)
                ed['address'] = ec1.text_input("Адрес ТП", value=ed['address'])
                ed['transformer_type'] = ec2.text_input(
                    "Трансформатор", value=ed['transformer_type'])

                # Поля Абонентов (динамически как в Add_TP)
                for s_idx, sec in enumerate(ed['sections']):
                    st.markdown(f"**Секция: {sec['number']}**")
                    for a_idx, sub in enumerate(sec['subscribers']):
                        with st.container(border=True):
                            st.write(f"Абонент: {sub['name']}")
                            ac1, ac2, ac3 = st.columns(3)
                            sub['name'] = ac1.text_input(
                                "Имя", value=sub['name'], key=f"e_n_{s_idx}_{a_idx}")
                            sub['number'] = ac2.text_input(
                                "Номер", value=sub['number'],
                                key=f"e_num_{s_idx}_{a_idx}")
                            sub['address'] = ac3.text_input(
                                "Адрес", value=sub['address'],
                                key=f"e_adr_{s_idx}_{a_idx}")

                            sub['fuse_rating'] = ac1.text_input(
                                "Предохранитель", value=sub['fuse_rating'], key=f"e_f_{s_idx}_{a_idx}")
                            sub['cable_brand'] = ac2.text_input(
                                "Марка кабеля", value=sub['cable_brand'], key=f"e_c_{s_idx}_{a_idx}")
                            sub['cable_length'] = ac3.number_input(
                                "Длина (м)", value=float(
                                    sub['cable_length']),
                                key=f"e_cl_{s_idx}_{a_idx}")

                            sub['ct_type'] = ac1.text_input(
                                "Тип ТТ", value=sub['ct_type'],
                                key=f"e_ctt_{s_idx}_{a_idx}")
                            sub['ct_rating'] = ac2.text_input(
                                "Ном. ТТ", value=sub['ct_rating'],
                                key=f"e_ctr_{s_idx}_{a_idx}")
                            sub['meter_type'] = ac3.text_input(
                                "Тип ПУ", value=sub['meter_type'], key=f"e_mt_{s_idx}_{a_idx}")

                # Кнопки сохранения
                sc1, sc2 = st.columns(2)
                if sc1.form_submit_button("✅ СОХРАНИТЬ ВСЁ"):
                    # Отправляем PATCH запрос
                    res = requests.patch(f"{API_URL}/tps/{tp['id']}", json=ed)
                    if res.status_code == 200:
                        st.success("Данные обновлены в базе!")
                        st.session_state.edit_mode = None
                        st.rerun()
                    else:
                        st.error(f"Ошибка: {res.text}")

                if sc2.form_submit_button("❌ ОТМЕНА"):
                    st.session_state.edit_mode = None
                    st.rerun()
