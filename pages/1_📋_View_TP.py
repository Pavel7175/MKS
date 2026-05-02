import streamlit as st
import requests
import pandas as pd
from ui_components import tp_fields, subscriber_fields

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Реестр ТП", layout="wide")
st.title("📋 Реестр и управление ТП")

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "edit_data" not in st.session_state:
    st.session_state.edit_data = {}

search_query = st.text_input(
    "🔍 Поиск по номеру ТП",
    placeholder="Например: ТП-500")

url = f"{API_URL}/tps/by-number/{search_query}" if search_query else f"{API_URL}/tps/"
try:
    res = requests.get(url)
    tps = []
    if res.status_code == 200:
        data = res.json()
        tps = [data] if isinstance(data, dict) else data
except BaseException:
    tps = []
for tp in tps:
    is_editing = st.session_state.edit_mode == tp['id']
    with st.expander(f"🏢 {tp['tp_number']} — {tp['address']}", expanded=is_editing):
        if not is_editing:
            # Просмотр ТП
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Район/Округ:** {tp['district']} / {tp['region']}")
            c2.write(f"**Трансформатор:** {tp['transformer_type']}")
            c3.write(
                f"**УСПД:** {tp['uspd_type']} | **Вкл:** {tp['commissioning_date']}")

            if st.button("📝 Редактировать всё", key=f"btn_ed_{tp['id']}"):
                st.session_state.edit_mode = tp['id']
                st.session_state.edit_data = tp.copy()
                st.rerun()

            for sec in tp['sections']:
                st.markdown(f"#### 📍 Луч: {sec['number']}")
                for sub in sec['subscribers']:
                    with st.container(border=True):
                        st.write(f"👤 **{sub['name']}** (№{sub['number']})")
                        sa1, sa2, sa3 = st.columns(3)
                        sa1.write(
                            f"**Кабель:** {sub['cable_brand']} ({sub['cable_length']}м)")
                        sa2.write(
                            f"**ТТ:** {sub['ct_type']} ({sub['ct_rating']})")
                        sa3.write(f"**ПУ:** {sub['meter_type']}")
                        if sub.get('buses'):
                            st.caption("🔗 Шины:")
                            st.table(pd.DataFrame(sub['buses'])[
                                     ['bus_type', 'bus_count']])
        else:
            # --- РЕЖИМ РЕДАКТИРОВАНИЯ ---
            ed = st.session_state.edit_data
            if st.button("➕ Добавить новый Луч", key=f"as_{tp['id']}"):
                ed['sections'].append(
                    {"number": "Новый", "assembly_type": "", "panel": "",
                     "subscribers": []})
                st.rerun()

            with st.form(f"f_ed_{tp['id']}"):
                ed = tp_fields(ed)
                for s_idx, sec in enumerate(ed['sections']):
                    st.divider()
                    col_h, col_d = st.columns([0.9, 0.1])
                    col_h.subheader(f"Луч: {sec['number']}")
                    if col_d.form_submit_button(
                            "🗑️", key=f"del_sec_{tp['id']}_{s_idx}"):
                        ed['sections'].pop(s_idx)
                        st.rerun()

                    sec['number'] = st.text_input(
                        "Имя луча", value=sec['number'],
                        key=f"sn_{tp['id']}_{s_idx}")

                    for a_idx, sub in enumerate(sec['subscribers']):
                        with st.container(border=True):
                            sub = subscriber_fields(
                                sub, key_prefix=f"esub_{tp['id']}_{s_idx}_{a_idx}")

                            # --- БЛОК ШИН (ИСПРАВЛЕНО) ---
                            st.write("🔗 **Шины абонента**")
                            if st.form_submit_button(
                                f"➕ Добавить шину абоненту {a_idx}",
                                    key=f"ab_{tp['id']}_{s_idx}_{a_idx}"):
                                sub.setdefault(
                                    'buses', []).append(
                                    {"bus_type": "", "bus_count": 1})
                                st.rerun()

                            for b_idx, bus in enumerate(sub.get('buses', [])):
                                bc1, bc2, bc3 = st.columns([0.6, 0.3, 0.1])
                                bus['bus_type'] = bc1.text_input(
                                    "Тип", value=bus['bus_type'], key=f"bt_{tp['id']}_{s_idx}_{a_idx}_{b_idx}")
                                bus['bus_count'] = bc2.number_input(
                                    "Кол-во", value=int(bus['bus_count']),
                                    key=f"bc_{tp['id']}_{s_idx}_{a_idx}_{b_idx}")
                                if bc3.form_submit_button(
                                        "❌", key=f"db_{tp['id']}_{s_idx}_{a_idx}_{b_idx}"):
                                    sub['buses'].pop(b_idx)
                                    st.rerun()

                    if st.form_submit_button(
                        f"👤 Добавить абонента в {sec['number']}",
                            use_container_width=True):
                        sec['subscribers'].append({"number": "",
                                                   "name": "",
                                                   "address": "",
                                                   "fuse_rating": "",
                                                   "cable_brand": "",
                                                   "cable_length": 0.0,
                                                   "ct_rating": "",
                                                   "ct_type": "",
                                                   "meter_type": "",
                                                   "buses": []})
                        st.rerun()

                if st.form_submit_button(
                    "✅ СОХРАНИТЬ ВСЁ",
                        use_container_width=True):
                    res = requests.patch(f"{API_URL}/tps/{tp['id']}", json=ed)
                    if res.status_code == 200:
                        st.success("Обновлено!")
                        st.session_state.edit_mode = None
                        st.rerun()
                if st.form_submit_button("❌ ОТМЕНА", use_container_width=True):
                    st.session_state.edit_mode = None
                    st.rerun()
