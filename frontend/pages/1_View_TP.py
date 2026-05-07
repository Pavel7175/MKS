import uuid

import requests
import streamlit as st
from ui_components import (
    bus_fields,
    section_fields,
    subscriber_fields,
    tp_fields,
)

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

API_URL = "http://127.0.0.1:8000"

# 1. ПЕРВЫМ ДЕЛОМ КОНФИГУРАЦИЯ
st.set_page_config(page_title="Реестр ТП", layout="wide")
st.title("📋 Реестр и управление ТП")

# 2. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ
if "page" not in st.session_state:
    st.session_state.page = 0

# 3. ЛОГИКА ПАГИНАЦИИ
limit = 10
offset = st.session_state.page * limit

# 4. ВЫВОД КНОПОК НАВИГАЦИИ
col1, col2, col3 = st.columns([1, 2, 1])
if col1.button("⬅️ Назад", disabled=(st.session_state.page == 0)):
    st.session_state.page -= 1
    st.rerun()

col2.write(f"Центр: Страница {st.session_state.page + 1}")

if col3.button("Вперед ➡️"):
    st.session_state.page += 1
    st.rerun()

# 5. ЗАПРОС К API
# Теперь параметры offset и limit полетят в роутер
url = f"{API_URL}/tps/?offset={offset}&limit={limit}"
res = requests.get(url)
tps = res.json() if res.status_code == 200 else []

# --- Инициализация состояния ---
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "edit_data" not in st.session_state:
    st.session_state.edit_data = {}

# search_query = st.text_input("🔍 Быстрый поиск по номеру ТП")
search_query = st.text_input("🔍 Поиск ТП",
                             placeholder="Введите номер ТП или адрес...")

# 2. Фильтрация списка (если что-то введено)
tps_list = tps
if search_query:
    tps_list = [
        tp for tp in tps_list
        if search_query.lower() in tp['tp_number'].lower()
        or search_query.lower() in tp['address'].lower()
    ]
    st.write(f"Найдено объектов: {len(tps_list)}")

if search_query:
    url = f"{API_URL}/tps/by-number/{search_query}"
else:
    # Используем пагинацию, только если нет поиска
    url = f"{API_URL}/tps/?offset={offset}&limit={limit}"

if len(tps) < limit and not search_query:
    st.info("Вы дошли до конца списка")
try:
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        # Если пришел один объект (из поиска), кладем его в список
        tps = [data] if isinstance(data, dict) else data
    else:
        tps = []
except BaseException:
    tps = []
# --- Основной цикл отрисовки ---
# ОПРЕДЕЛЯЕМ ДИАЛОГ ОДИН РАЗ ВНЕ ЦИКЛА


@st.dialog("Удаление объекта")
def delete_confirm_dialog(tp_to_delete):
    st.error(
        f"Вы уверены, что хотите полностью удалить ТП №{tp_to_delete['tp_number']}?")
    st.write(f"Адрес: {tp_to_delete['address']}")

    dcol1, dcol2 = st.columns(2)
    if dcol1.button("Отмена", use_container_width=True):
        st.rerun()

    if dcol2.button("🔥 Да, удалить", type="primary", use_container_width=True):
        res = requests.delete(f"{API_URL}/tps/{tp_to_delete['id']}")
        if res.status_code == 200:
            st.success("Удалено успешно!")
            # Очищаем состояние редактирования на всякий случай
            st.session_state.edit_mode = None
            st.rerun()  # Теперь просто перегружаем страницу со списком
        else:
            st.error(
                f"Ошибка сервера: {res.json().get('detail', 'Неизвестная ошибка')}")


# 1. Поле поиска в самом верху
# search_query = st.text_input("🔍 Поиск ТП",
#                              placeholder="Введите номер ТП или адрес...")

# # 2. Фильтрация списка (если что-то введено)
# tps_list = tps
# if search_query:
#     tps_list = [
#         tp for tp in tps_list
#         if search_query.lower() in tp['tp_number'].lower()
#         or search_query.lower() in tp['address'].lower()
#     ]
#     st.write(f"Найдено объектов: {len(tps_list)}")

for tp in tps_list:
    tp_id = tp['id']
    is_editing = st.session_state.edit_mode == tp_id

    with st.expander(f"🏢 {tp['tp_number']} — {tp['address']}", expanded=is_editing or bool(search_query)):
        if not is_editing:
            # --- ПРОСМОТР ---
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Район/Округ:** {tp['district']} / {tp['region']}")
            c2.write(f"**Трансформатор:** {tp['transformer_type']}")
            c3.write(
                f"**УСПД:** {tp['uspd_type']} | **Вкл:** {tp['commissioning_date']}")

            if st.button("📝 Редактировать", key=f"view_edit_{tp_id}"):
                st.session_state.edit_mode = tp_id
                st.session_state.edit_data = tp.copy()
                st.rerun()
            # --- АВТОМАТИЧЕСКАЯ ССЫЛКА (Район / Номер ТП) ---

            # 1. Базовый путь к папке "Рабочее проектирование"
            base_url = "https://disk.yandex.ru/client/disk/СТОК РД/МКС АСКУЭ ТП 2021/Рабочее проектирование/"

            # 2. Берем Район и Номер ТП из данных (ed)
            dist = tp.get('district', '')
            tp_num = tp.get('tp_number', '')

            # 3. Отрисовка кнопок управления
            c_space, c_docs, c_del = st.columns([0.6, 0.2, 0.2])

            if dist and tp_num:
                # Собираем путь: база / Район / Номер ТП
                # Например: .../Рабочее проектирование/17/16172
                full_url = f"{base_url}{dist}/{tp_num}"

                c_docs.link_button(
                    "📂 Документы",
                    full_url,
                    use_container_width=True,
                    help=f"Открыть папку ТП {tp_num} в районе {dist}"
                )
            else:
                # Если чего-то не хватает, пишем подсказку
                reason = "Нет района" if not dist else "Нет номера"
                c_docs.button(
                    f"📂 {reason}",
                    disabled=True,
                    use_container_width=True)

            for sec in tp['sections']:
                with st.expander(f"📍 Луч: {sec['number']} (Панель: {sec['panel']})"):
                    st.write(f"**Тип сборки:** {sec['assembly_type']}")
                    for sub in sec['subscribers']:
                        with st.container(border=True):
                            st.write(f"👤 **{sub['number']}** ({sub['name']})")

                            st.caption(
                                f"ТТ: {sub['ct_type']} ({sub['ct_rating']}) | ПУ: {sub['meter_type']}")
                            if sub.get('buses'):
                                bus_list = [
                                    f"{b['bus_type']} ({b['bus_count']} шт.)"
                                    for b in sub['buses']
                                    if b.get('bus_type')]
                                if bus_list:
                                    bus_str = ", ".join(bus_list)
                                    st.caption(f"**Шины:** {bus_str}")

        else:

            # --- Кнопка УДАЛЕНИЯ всей ТП (над формой редактирования) ---
            # Кнопка удаления

            # 2. Твоя кнопка удаления
            if c_del.button(
                "🗑️ Удалить ТП",
                key=f"del_tp_{tp_id}",
                type="secondary",
                    use_container_width=True):
                delete_confirm_dialog(tp)

            # --- РЕДАКТИРОВАНИЕ ---
            st.warning(f"🛠 Редактирование {tp['tp_number']}")
            ed = st.session_state.edit_data

            if st.button("➕ Добавить новый Луч", key=f"add_sec_{tp_id}"):
                ed['sections'].append(
                    {"number": "Новый", "assembly_type": "", "panel": "",
                     "subscribers": []})
                st.rerun()

            with st.form(f"f_edit_{tp_id}"):
                ed = tp_fields(ed)  # Поля ТП

                for s_idx, sec in enumerate(ed['sections']):
                    with st.expander(f"📍 Луч: {sec['number']}", expanded=True):

                        c_h, c_d = st.columns([0.9, 0.1])
                        if c_d.form_submit_button(
                                "🗑️", key=f"ds_{tp_id}_{s_idx}"):
                            ed['sections'].pop(s_idx)
                            st.rerun()

                        # ДОБАВИЛИ ПАНЕЛЬ И СБОРКУ
                        sec = section_fields(
                            sec, key_prefix=f"es_{tp_id}_{s_idx}")

                        for a_idx, sub in enumerate(
                                sec.get('subscribers', [])):
                            with st.expander(f"👤 {sub['name'] if sub['name'] else 'Новый'}", expanded=False):
                                if st.form_submit_button(
                                    "❌ Удалить абонента",
                                        key=f"dsub_{tp_id}_{s_idx}_{a_idx}"):
                                    sec['subscribers'].pop(a_idx)
                                    st.rerun()

                                sub = subscriber_fields(
                                    sub, key_prefix=f"esub_{tp_id}_{s_idx}_{a_idx}")

                                # --- ШИНЫ ВНУТРИ АБОНЕНТА ---
                                st.write("🔗 **Шины**")
                                if st.form_submit_button(
                                        "➕ Добавить шину", key=f"ab_{tp_id}_{s_idx}_{a_idx}"):
                                    sub.setdefault(
                                        'buses', []).append(
                                        {"bus_type": "", "bus_count": 1})
                                    st.rerun()

                                # for b_idx, bus in enumerate(
                                #         sub.get('buses', [])):
                                #     # Вызываем готовую функцию, которая уже
                                #     # умеет делать выпадающий список
                                #     bc3 = bus_fields(
                                # bus,
                                # key_prefix=f"eb_{tp_id}_{s_idx}_{a_idx}_{b_idx}")

                                #     if bc3.form_submit_button(
                                #             "❌", key=f"db_{tp_id}_{s_idx}_{a_idx}_{b_idx}"):
                                #         # Находим и удаляем именно этот объект
                                #         # шины
                                #         bus_to_delete = sub['buses'][b_idx]
                                #         sub['buses'].remove(bus_to_delete)
                                #         st.rerun()

                                if "buses" not in sub:
                                    sub["buses"] = []

                                # 1. Присваиваем каждой шине постоянный скрытый
                                # ID, если его нет
                                for bus in sub["buses"]:
                                    if "_id" not in bus:
                                        bus["_id"] = str(uuid.uuid4())

                                # 2. Отрисовка
                                # Используем list() для создания копии списка
                                # на время итерации
                                for bus in list(sub["buses"]):
                                    b_unique_id = bus["_id"]

                                    # Передаем уникальный ID в функцию полей
                                    bc3 = bus_fields(
                                        bus, key_prefix=f"bus_{b_unique_id}")

                                    # Кнопка удаления привязана к конкретному
                                    # ID, а не к позиции в списке
                                    if bc3.form_submit_button(
                                            "❌", key=f"del_{b_unique_id}"):
                                        # Удаляем из оригинального списка
                                        # именно эту шину по её ID
                                        sub['buses'] = [
                                            b for b in sub['buses'] if b.get('_id') != b_unique_id]
                                        st.rerun()

                        if st.form_submit_button(
                            "👤 Добавить абонента",
                            key=f"asb_{tp_id}_{s_idx}",
                                use_container_width=True):
                            sec['subscribers'].append(
                                {
                                    "number": "",
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

                sc1, sc2 = st.columns(2)
                if sc1.form_submit_button(
                        "✅ СОХРАНИТЬ", use_container_width=True):
                    res = requests.patch(f"{API_URL}/tps/{tp_id}", json=ed)
                    if res.status_code == 200:
                        st.success("Обновлено!")
                        st.session_state.edit_mode = None
                        st.rerun()
                if sc2.form_submit_button(
                        "❌ ОТМЕНА", use_container_width=True):
                    st.session_state.edit_mode = None
                    st.rerun()
