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
    st.session_state.edit_data = {}    # Временный буфер данных для формы

search_query = st.text_input("🔍 Быстрый поиск по номеру ТП")
url = f"{API_URL}/tps/by-number/{search_query}" if search_query else f"{API_URL}/tps/"

res = requests.get(url)
if res.status_code == 200:
    data = res.json()
    tps = [data] if isinstance(data, dict) else data
else:
    tps = []
    st.info("Данные не найдены или введите номер ТП.")
for tp in tps:
    is_editing = st.session_state.edit_mode == tp['id']

    with st.expander(f"🏢 {tp['tp_number']} — {tp['address']}", expanded=is_editing or bool(search_query)):
        if not is_editing:
            # Карточка ТП
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Район/Округ:** {tp['district']} / {tp['region']}")
            c2.write(
                f"**Трансформатор:** {tp['transformer_type']} ({tp['voltage']})")
            c3.write(
                f"**УСПД:** {tp['uspd_type']} | **Вкл:** {tp['commissioning_date']}")

            if st.button(
                f"📝 Редактировать ТП и структуру",
                    key=f"btn_edit_{tp['id']}"):
                st.session_state.edit_mode = tp['id']
                st.session_state.edit_data = tp  # Загружаем всё дерево данных в буфер
                st.rerun()

            # Отображение вложенной структуры
            for sec in tp['sections']:
                st.markdown(
                    f"--- \n#### 📍 Секция: {sec['number']} (Панель: {sec['panel']})")
                for sub in sec['subscribers']:
                    with st.container(border=True):
                        st.write(
                            f"👤 **{sub['name']}** (№{sub['number']}) | {sub['address']}")
                        sa1, sa2, sa3 = st.columns(3)
                        sa1.write(
                            f"**Кабель:** {sub['cable_brand']} ({sub['cable_length']}м)")
                        sa2.write(
                            f"**ТТ:** {sub['ct_type']} ({sub['ct_rating']})")
                        sa3.write(
                            f"**ПУ:** {sub['meter_type']} | **Предохранитель:** {sub['fuse_rating']}")

                        if sub.get('buses'):
                            st.caption("Шины:")
                            st.dataframe(
                                pd.DataFrame(sub['buses'])
                                [['bus_type', 'bus_count']],
                                hide_index=True)
        else:
            # РЕЖИМ РЕДАКТИРОВАНИЯ ВСЕХ ПОЛЕЙ
            st.warning(f"🛠 Редактирование ТП: {tp['tp_number']}")
            ed = st.session_state.edit_data  # Сокращение для удобства

            with st.form(f"full_edit_form_{tp['id']}"):
                # 1. Поля ТП
                ec1, ec2, ec3 = st.columns(3)
                ed['address'] = ec1.text_input("Адрес ТП", value=ed['address'])
                ed['district'] = ec2.text_input("Район", value=ed['district'])
                ed['transformer_type'] = ec3.text_input(
                    "Трансформатор", value=ed['transformer_type'])

                # 2. Поля Секций и Абонентов
                for s_idx, sec in enumerate(ed['sections']):
                    st.markdown(f"**Настройка секции: {sec['number']}**")
                    sec['panel'] = st.text_input(
                        f"Панель секции", value=sec['panel'], key=f"e_p_{s_idx}")

                    for a_idx, sub in enumerate(sec['subscribers']):
                        with st.container(border=True):
                            st.write(f"Абонент: {sub['name']}")
                            ac1, ac2, ac3 = st.columns(3)
                            sub['name'] = ac1.text_input(
                                "Имя", value=sub['name'], key=f"e_sn_{s_idx}_{a_idx}")
                            sub['cable_brand'] = ac2.text_input(
                                "Кабель", value=sub['cable_brand'], key=f"e_sc_{s_idx}_{a_idx}")
                            sub['meter_type'] = ac3.text_input(
                                "ПУ", value=sub['meter_type'], key=f"e_sm_{s_idx}_{a_idx}")

                # Кнопки сохранения
                sc1, sc2 = st.columns(2)
                # В блоке сохранения (Часть 3)
                if sc1.form_submit_button("✅ СОХРАНИТЬ ИЗМЕНЕНИЯ"):
                    with st.spinner('Синхронизация с базой данных...'):
                        try:
                            # Важно: используем json=ed, где ed — это полный
                            # словарь из session_state
                            res = requests.patch(
                                f"{API_URL}/tps/{tp['id']}", json=ed)

                            if res.status_code == 200:
                                st.toast(
                                    f"ТП {tp['tp_number']} обновлена!", icon="✅")
                                st.success("Данные успешно записаны в базу.")
                                st.session_state.edit_mode = None
                                # Принудительно очищаем кэш запросов, если он
                                # есть
                                st.rerun()
                            else:
                                st.error(f"Ошибка сохранения: {res.text}")
                        except Exception as e:
                            st.error(f"Ошибка связи: {e}")

                # В блоке вывода данных абонента (чтобы видеть ВСЁ)
                # Проверь, что в цикле прописаны именно эти строки:
                st.write(
                    f"**ТТ:** {sub.get('ct_type')} ({sub.get('ct_rating')}) | **ПУ:** {sub.get('meter_type')}")
                st.write(
                    f"**Кабель:** {sub.get('cable_brand')} | **Длина:** {sub.get('cable_length')} м")
                st.write(f"**Предохранитель:** {sub.get('fuse_rating')}")

                if sc2.form_submit_button("❌ ОТМЕНА"):
                    st.session_state.edit_mode = None
                    st.rerun()
