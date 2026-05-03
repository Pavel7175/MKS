import streamlit as st
import requests
import copy
import uuid
from ui_components import tp_fields, subscriber_fields, bus_fields, section_fields

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Добавить ТП", layout="wide")
st.title("➕ Добавление новой ТП")

if "new_tp" not in st.session_state:
    st.session_state.new_tp = {
        "tp_number": "", "district": "", "region": "", "address": "",
        "voltage": "10/0.4 кВ", "transformer_type": "", "uspd_type": "",
        "execution_type": "", "commissioning_date": None,
        "sections": []
    }

if "sub_buffer" not in st.session_state:
    st.session_state.sub_buffer = None

tp = st.session_state.new_tp

if st.button("➕ Добавить новый Луч"):
    tp["sections"].append(
        {"number": f"Луч {len(tp['sections'])+1}", "panel": "",
         "assembly_type": "", "subscribers": []})
    st.rerun()
with st.form("add_tp_form"):
    st.subheader("🏢 Характеристики подстанции")
    tp["tp_number"] = st.text_input("📝 Номер ТП", value=tp["tp_number"])
    tp.update(tp_fields(tp))

    for s_idx, sec in enumerate(tp["sections"]):
        st.divider()
        with st.expander(f"📍 {sec['number']}", expanded=True):
            sec.update(section_fields(sec, key_prefix=f"add_s_{s_idx}"))

            for a_idx, sub in enumerate(sec["subscribers"]):
                with st.container(border=True):
                    # ПАНЕЛЬ УПРАВЛЕНИЯ АБОНЕНТОМ
                    c_h, c_cp, c_ps, c_dl = st.columns([0.5, 0.15, 0.15, 0.1])
                    c_h.write(f"👤 **Абонент №{a_idx + 1}**")

                    # 📋 КОПИРОВАТЬ
                    if c_cp.form_submit_button("📋", key=f"cp_{s_idx}_{a_idx}"):
                        st.session_state.sub_buffer = copy.deepcopy(sub)
                        st.toast("Данные абонента скопированы")

                    # 📥 ВСТАВИТЬ (С ПОЛНОЙ ОЧИСТКОЙ)
                    if c_ps.form_submit_button("📥", key=f"ps_{s_idx}_{a_idx}"):
                        if st.session_state.sub_buffer:
                            # 1. Глубокое копирование данных из буфера
                            source = copy.deepcopy(st.session_state.sub_buffer)

                            # 2. Сохраняем то, что не должно меняться
                            old_name = sub.get("name", "")
                            old_num = sub.get("number", "")

                            # 3. Полная замена объекта в списке
                            sec["subscribers"][a_idx] = source
                            sec["subscribers"][a_idx]["name"] = old_name
                            sec["subscribers"][a_idx]["number"] = old_num

                            # 4. ЖЕСТКАЯ ОЧИСТКА ВСЕХ КЛЮЧЕЙ ЭТОГО АБОНЕНТА И ЕГО ШИН
                            # Мы удаляем всё, что связано с этим индексом
                            # абонента
                            target_prefix = f"_{s_idx}_{a_idx}"
                            keys_to_flush = [
                                str(k) for k in st.session_state.keys()
                                if target_prefix in str(k)
                            ]
                            for k in keys_to_flush:
                                if k in st.session_state:
                                    del st.session_state[k]

                            st.rerun()
                        else:
                            st.warning("Буфер пуст")

                    if c_dl.form_submit_button(
                            "🗑️", key=f"dl_{s_idx}_{a_idx}"):
                        sec["subscribers"].pop(a_idx)
                        st.rerun()

                    # Отрисовка полей
                    sub.update(
                        subscriber_fields(
                            sub, key_prefix=f"asub_{s_idx}_{a_idx}"))

                    st.write("🔗 **Шины**")
                    for b_idx, bus in enumerate(sub.get("buses", [])):
                        bus_fields(
                            bus, key_prefix=f"ab_{s_idx}_{a_idx}_{b_idx}")

                    if st.form_submit_button(
                            f"➕ Добавить шину", key=f"abn_{s_idx}_{a_idx}"):
                        sub.setdefault(
                            "buses", []).append(
                            {"bus_type": "", "bus_count": 1})
                        st.rerun()

            if st.form_submit_button(
                f"👤 Добавить абонента",
                use_container_width=True,
                    key=f"as_btn_{s_idx}"):
                sec["subscribers"].append(
                    {"name": "", "number": "", "address": "", "ct_type": "",
                     "ct_rating": "", "meter_type": "", "fuse_rating": "",
                     "cable_brand": "", "cable_length": 0.0, "buses": []})
                st.rerun()

    if st.form_submit_button("💾 СОХРАНИТЬ ТП", use_container_width=True):
        if not tp["tp_number"]:
            st.error("Введите номер ТП!")
        else:
            payload = copy.deepcopy(tp)
            if payload.get("commissioning_date"):
                payload["commissioning_date"] = str(
                    payload["commissioning_date"])
            res = requests.post(f"{API_URL}/tps/", json=payload)
            if res.status_code == 200:
                st.success("Успешно сохранено!")
                st.session_state.new_tp = {"tp_number": "", "sections": []}
                st.rerun()
