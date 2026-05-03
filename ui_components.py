import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"


def render_db_selectbox(label, category, current_value, key):
    """Выпадающий список, работающий с базой через API"""
    options = []
    try:
        response = requests.get(f"{API_URL}/refs/{category.upper()}")
        if response.status_code == 200:
            options = response.json()
    except Exception:
        options = []

    if not options:
        options = ["-- Справочник пуст --"]

    # Чтобы не было ошибки, если в базе есть значение, которого нет в текущем
    # списке
    if current_value and current_value not in options:
        options.append(current_value)

    try:
        idx = options.index(current_value) if current_value in options else 0
    except ValueError:
        idx = 0

    return st.selectbox(label, options=options, index=idx, key=f"sel_{key}")


def tp_fields(data=None):
    """Поля характеристик ТП"""
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
    # УСПД — Выпадающий список
    res['uspd_type'] = render_db_selectbox(
        "Тип УСПД", "USPD", res.get(
            'uspd_type', ""), "tp_uspd")

    return res


def section_fields(sec, key_prefix):
    """Поля луча: Название, Панель и Сборка в один ряд"""
    col1, col2, col3 = st.columns(3)

    sec['number'] = col1.text_input(
        "Название луча", value=sec.get(
            'number', ""), key=f"{key_prefix}_sn")

    # Панель — Выпадающий список
    with col2:
        sec['panel'] = render_db_selectbox(
            "Панель", "PANEL", sec.get(
                'panel', ""), f"{key_prefix}_p")

    # Тип сборки — Выпадающий список
    with col3:
        sec['assembly_type'] = render_db_selectbox(
            "Тип сборки", "ASSEMBLY", sec.get(
                'assembly_type', ""), f"{key_prefix}_at")

    return sec


def subscriber_fields(sub, key_prefix):
    """Все тех. поля абонента: ТТ, ПУ, Кабель"""
    ac1, ac2, ac3 = st.columns(3)

    sub['name'] = ac1.text_input(
        "ФИО / Наименование",
        value=sub.get(
            'name',
            ""),
        key=f"{key_prefix}_n")
    sub['number'] = ac2.text_input(
        "Номер абонента", value=sub.get(
            'number', ""), key=f"{key_prefix}_num")
    sub['address'] = ac3.text_input(
        "Адрес абонента", value=sub.get(
            'address', ""), key=f"{key_prefix}_adr")

    sub['fuse_rating'] = ac1.text_input(
        "Предохранитель", value=sub.get(
            'fuse_rating', ""), key=f"{key_prefix}_f")
    sub['cable_brand'] = ac2.text_input(
        "Марка кабеля", value=sub.get(
            'cable_brand', ""), key=f"{key_prefix}_c")
    sub['cable_length'] = ac3.number_input(
        "Длина (м)",
        value=float(
            sub.get(
                'cable_length',
                0)),
        key=f"{key_prefix}_l")

    # ТТ и ПУ — Выпадающие списки
    with ac1:
        sub['ct_type'] = render_db_selectbox(
            "Тип ТТ", "TT_TYPE", sub.get(
                'ct_type', ""), f"{key_prefix}_ctt")
    with ac2:
        sub['ct_rating'] = render_db_selectbox(
            "Номинал ТТ", "TT_RATING", sub.get(
                'ct_rating', ""), f"{key_prefix}_ctr")
    with ac3:
        sub['meter_type'] = render_db_selectbox(
            "Тип ПУ (Счетчик)", "PU_TYPE", sub.get(
                'meter_type', ""), f"{key_prefix}_mt")

    return sub


def bus_fields(bus, key_prefix):
    """Поля шин: Тип и количество"""
    bc1, bc2, bc3 = st.columns([0.6, 0.3, 0.1])

    # Тип шины — Выпадающий список
    with bc1:
        bus['bus_type'] = render_db_selectbox(
            "Тип шины", "BUS_TYPE", bus.get(
                'bus_type', ""), f"{key_prefix}_bt")

    bus['bus_count'] = bc2.number_input(
        "Кол-во", value=int(bus.get('bus_count', 1)),
        min_value=1, key=f"{key_prefix}_bc")

    return bc3  # Возвращаем колонку для кнопки удаления
