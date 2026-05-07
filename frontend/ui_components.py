import requests
import streamlit as st
from logic import get_match_tt

API_URL = "http://127.0.0.1:8000"


def get_db_options(category):
    """Вспомогательная функция для получения списка из БД через FastAPI"""
    try:
        # category — это TT_TYPE, TT_RATING, PU_TYPE и т.д.
        response = requests.get(f"{API_URL}/refs/{category.upper()}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Ошибка получения справочника {category}: {e}")
        return []
    return []

# def render_db_selectbox(label, category, current_value, key):
#     options = []
#     try:
#         response = requests.get(f"{API_URL}/refs/{category.upper()}")
#         if response.status_code == 200:
#             options = response.json()
#     except BaseException:
#         options = []
#     if not options:
#         options = ["-- Справочник пуст --"]
#     if current_value and current_value not in options:
#         options.append(current_value)
#     if key in st.session_state:
#         current_value = st.session_state[key]
#     try:
#         idx = options.index(current_value) if current_value in options else 0
#     except BaseException:
#         idx = 0
#     # Используем key напрямую, так как префикс уже содержит уникальность
#     return st.selectbox(label, options=options, index=idx, key=key)


def render_db_selectbox(label, category, current_value, key):
    options = get_db_options(category)
    if not options:
        options = ["-- Справочник пуст --"]

    # ВАЖНО: Убираем отсюда все чтения из st.session_state[key]
    # Виджет должен полагаться только на аргумент current_value

    if current_value and current_value not in options:
        options.append(current_value)

    try:
        idx = options.index(current_value) if current_value in options else 0
    except BaseException:
        idx = 0

    return st.selectbox(label, options=options, index=idx, key=key)


def tp_fields(data=None):
    res = data or {}
    c1, c2, c3 = st.columns(3)
    res['address'] = c1.text_input(
        "Адрес ТП", value=res.get(
            'address', ""), key="tp_adr")
    res['district'] = c1.text_input(
        "Район", value=res.get(
            'district', ""), key="tp_dist")
    res['region'] = c2.text_input(
        "Округ", value=res.get(
            'region', ""), key="tp_reg")
    res['voltage'] = c2.text_input(
        "Напряжение", value=res.get(
            'voltage', "10/0.4 кВ"), key="tp_volt")
    res['transformer_type'] = c3.text_input(
        "Тип трансформатора", value=res.get(
            'transformer_type', ""), key="tp_tr")
    res['execution_type'] = c3.text_input(
        "Исполнение ТП", value=res.get(
            'execution_type', "ТК-2х400"))
    res['uspd_type'] = render_db_selectbox(
        "Тип УСПД", "USPD", res.get(
            'uspd_type', ""), "tp_uspd_sel")
    return res


def section_fields(sec, key_prefix):
    col1, col2, col3 = st.columns(3)
    sec['number'] = col1.text_input(
        "Название луча", value=sec.get(
            'number', ""), key=f"{key_prefix}_sn")
    with col2:
        sec['panel'] = render_db_selectbox(
            "Панель", "PANEL", sec.get(
                'panel', ""), f"{key_prefix}_p")
    with col3:
        sec['assembly_type'] = render_db_selectbox(
            "Тип сборки", "ASSEMBLY", sec.get(
                'assembly_type', ""), f"{key_prefix}_at")
    return sec


def subscriber_fields(sub, key_prefix):
    ac1, ac2, ac3 = st.columns(3)

    # 1. Текстовые поля
    sub['name'] = ac1.text_input(
        "ФИО", value=sub.get('name', ""),
        key=f"{key_prefix}_n")
    sub['number'] = ac2.text_input(
        "№ Абонента", value=sub.get(
            'number', ""), key=f"{key_prefix}_num")
    sub['address'] = ac3.text_input(
        "Адрес", value=sub.get('address', ""),
        key=f"{key_prefix}_adr")

    # --- ЛОГИКА АВТОПОДБОРА ---
    f_key = f"{key_prefix}_f"
    # Берем то, что ввел пользователь СЕЙЧАС
    input_fuse = st.session_state.get(f_key, sub.get('fuse_rating', ""))

    # Если номинал изменился - ищем ТТ в базе
    if input_fuse != sub.get('fuse_rating', ""):
        sub['fuse_rating'] = input_fuse
        match = get_match_tt(input_fuse)
        if match:
            sub['ct_rating'] = match  # Обновляем значение в словаре ТУТ

    # Отрисовываем само поле предохранителя
    sub['fuse_rating'] = ac1.text_input(
        "Предохранитель (А)",
        value=sub.get('fuse_rating', ""),
        key=f_key)
    # --------------------------

    sub['cable_brand'] = ac2.text_input(
        "Кабель", value=sub.get('cable_brand', ""),
        key=f"{key_prefix}_c")
    sub['cable_length'] = ac3.number_input(
        "Длина (м)",
        value=float(
            sub.get(
                'cable_length',
                0.0)),
        key=f"{key_prefix}_l")

    with ac1:
        sub['ct_type'] = render_db_selectbox(
            "Тип ТТ", "TT_TYPE", sub.get(
                'ct_type', ""), f"{key_prefix}_ctt")
    with ac2:
        # Теперь селектбокс возьмет sub['ct_rating'], который мы обновили выше!
        sub['ct_rating'] = render_db_selectbox(
            "Ном. ТТ", "TT_RATING", sub.get(
                'ct_rating', ""), f"{key_prefix}_ctr")
    with ac3:
        sub['meter_type'] = render_db_selectbox(
            "ПУ", "PU_TYPE", sub.get(
                'meter_type', ""), f"{key_prefix}_mt")

    return sub


def bus_fields(bus, key_prefix):
    bc1, bc2, bc3 = st.columns([0.6, 0.3, 0.1])
    with bc1:
        bus['bus_type'] = render_db_selectbox(
            "Тип шины", "BUS_TYPE", bus.get(
                'bus_type', ""), f"{key_prefix}_bt")
    # ГЛАВНЫЙ ФИКС: Явное приведение к int и использование уникального ключа
    bus['bus_count'] = bc2.number_input(
        "Кол-во",
        min_value=1,
        value=int(bus.get('bus_count', 1)),
        key=f"{key_prefix}_bc"
    )
    return bc3
