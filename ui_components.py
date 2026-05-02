import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"


def render_db_selectbox(label, category, current_value, key):
    """Выпадающий список, который берет данные ТОЛЬКО из БД (таблица Reference)"""
    options = []
    try:
        # Запрос к твоему API: routers/refs.py
        response = requests.get(f"{API_URL}/refs/{category.upper()}")
        if response.status_code == 200:
            options = response.json()
    except Exception:
        options = []

    # Если в базе пусто по этой категории
    if not options:
        options = ["-- Справочник пуст --"]

    # Добавляем текущее значение, если оно уже было сохранено, но его нет в
    # списке
    if current_value and current_value not in options:
        options.append(current_value)

    # Находим индекс для отображения текущего значения
    try:
        idx = options.index(current_value) if current_value in options else 0
    except ValueError:
        idx = 0

    return st.selectbox(label, options=options, index=idx, key=f"sel_{key}")


def tp_fields(data=None):
    res = data or {}
    c1, c2, c3 = st.columns(3)
    res['address'] = c1.text_input("Адрес ТП", value=res.get('address', ""))
    res['district'] = c1.text_input("Район", value=res.get('district', ""))
    res['region'] = c2.text_input("Округ", value=res.get('region', ""))
    res['voltage'] = c2.text_input(
        "Напряжение", value=res.get(
            'voltage', "10/0.4 кВ"))
    res['transformer_type'] = c3.text_input(
        "Тип трансформатора", value=res.get(
            'transformer_type', ""))

    # ВЫПАДАЮЩИЙ СПИСОК: УСПД
    res['uspd_type'] = render_db_selectbox(
        "Тип УСПД", "USPD", res.get(
            'uspd_type', ""), "tp_uspd")
    return res


def subscriber_fields(sub, key_prefix):
    ac1, ac2, ac3, ac4, ac5 = st.columns(5)
    sub['number'] = ac1.text_input(
        "Номер", value=sub.get('number', ""),
        key=f"{key_prefix}_num")
    sub['name'] = ac2.text_input(
        "Имя", value=sub.get('name', ""),
        key=f"{key_prefix}_n")
    sub['address'] = ac3.text_input(
        "Адрес", value=sub.get('address', ""),
        key=f"{key_prefix}_adr")

    sub['cable_brand'] = ac4.text_input(
        "Марка кабеля", value=sub.get(
            'cable_brand', ""), key=f"{key_prefix}_c")
    sub['cable_length'] = ac5.number_input(
        "Длина (м)",
        value=float(
            sub.get(
                'cable_length',
                0)),
        key=f"{key_prefix}_l")

    sub['fuse_rating'] = ac1.text_input(
        "Предохранитель", value=sub.get(
            'fuse_rating', ""), key=f"{key_prefix}_f")

    # ВЫПАДАЮЩИЕ СПИСКИ: ТТ (Тип и Номинал)
    with ac2:
        sub['ct_type'] = render_db_selectbox(
            "Тип ТТ", "TT_TYPE", sub.get(
                'ct_type', ""), f"{key_prefix}_ctt")
    with ac3:
        sub['ct_rating'] = render_db_selectbox(
            "Номинал ТТ", "TT_RATING", sub.get(
                'ct_rating', ""), f"{key_prefix}_ctr")

    # ВЫПАДАЮЩИЙ СПИСОК: СЧЕТЧИК (ПУ)
    with ac4:
        sub['meter_type'] = render_db_selectbox(
            "Тип ПУ", "PU_TYPE", sub.get(
                'meter_type', ""), f"{key_prefix}_mt")
    return sub


def bus_fields(bus, key_prefix):
    bc1, bc2, bc3 = st.columns([0.6, 0.3, 0.1])

    # ВЫПАДАЮЩИЙ СПИСОК: ТИП ШИНЫ
    with bc1:
        bus['bus_type'] = render_db_selectbox(
            "Тип шины", "BUS_TYPE", bus.get(
                'bus_type', ""), f"{key_prefix}_bt")
    with bc2:
        bus['bus_count'] = st.number_input(
            "Кол-во", value=int(bus.get('bus_count', 1)),
            min_value=1, key=f"{key_prefix}_bc")
    return bc3


def section_fields(sec, key_prefix):
    """Поля луча: Название, Панель и Тип сборки (все из БД)"""
    col_s1, col_s2, col_s3 = st.columns(3)  # Разделим на 3 колонки для красоты

    with col_s1:
        sec['number'] = st.text_input(
            "Название луча",
            value=sec.get('number', ""),
            key=f"{key_prefix}_sn"
        )

    # ПАНЕЛЬ — ВЫПАДАЮЩИЙ СПИСОК
    with col_s2:
        sec['panel'] = render_db_selectbox(
            "Панель",
            "PANEL",
            sec.get('panel', ""),
            f"{key_prefix}_sp"
        )

    # ТИП СБОРКИ — ТЕПЕРЬ ТОЖЕ ВЫПАДАЮЩИЙ СПИСОК
    with col_s3:
        sec['assembly_type'] = render_db_selectbox(
            "Тип сборки",
            "ASSEMBLY",
            sec.get('assembly_type', ""),
            f"{key_prefix}_at"
        )
        return sec
