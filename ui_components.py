import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"


def render_editable_selectbox(label, category, current_value, key):
    """Выпадающий список, работающий с твоим роутером /refs/"""
    options = []
    category_key = category.upper()

    try:
        # Запрос к твоему эндпоинту @router.get("/{category}")
        response = requests.get(f"{API_URL}/refs/{category_key}")
        if response.status_code == 200:
            options = response.json()
    except BaseException:
        pass

    # Если база пустая, выводим заглушку
    if not options:
        options = ["-- База пуста --"]

    display_options = options + ["➕ Добавить новое..."]

    # Пытаемся найти текущее значение в списке для корректного отображения
    start_idx = 0
    if current_value in options:
        start_idx = options.index(current_value)

    selected = st.selectbox(
        label,
        options=display_options,
        index=start_idx,
        key=f"sel_{key}")

    # Если пользователь хочет добавить новое значение
    if selected == "➕ Добавить новое...":
        new_val = st.text_input(
            f"Новое значение для '{label}'",
            key=f"input_{key}")
        if st.button("Сохранить в справочник", key=f"btn_{key}"):
            if new_val:
                # Запрос к твоему эндпоинту @router.post("/")
                payload = {"category": category_key, "value": new_val}
                res = requests.post(f"{API_URL}/refs/", json=payload)
                if res.status_code == 200:
                    st.success(f"'{new_val}' сохранено!")
                    st.rerun()
                else:
                    st.error("Ошибка при сохранении")
        return current_value

    return selected if selected != "-- База пуста --" else ""


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

    # СПРАВОЧНИК: УСПД
    res['uspd_type'] = render_editable_selectbox(
        "Тип УСПД", "USPD", res.get('uspd_type', ""), "tp_uspd")
    return res


def section_fields(sec, key_prefix):
    c1, c2 = st.columns(2)
    sec['number'] = c1.text_input(
        "Название луча", value=sec.get(
            'number', ""), key=f"{key_prefix}_sn")
    # СПРАВОЧНИК: ПАНЕЛЬ
    sec['panel'] = render_editable_selectbox(
        "Панель", "PANEL", sec.get(
            'panel', ""), f"{key_prefix}_p")
    sec['assembly_type'] = st.text_input(
        "Тип сборки", value=sec.get(
            'assembly_type', ""), key=f"{key_prefix}_at")
    return sec


def subscriber_fields(sub, key_prefix):
    ac1, ac2, ac3 = st.columns(3)
    sub['name'] = ac1.text_input(
        "Имя", value=sub.get('name', ""),
        key=f"{key_prefix}_n")
    sub['number'] = ac2.text_input(
        "Номер", value=sub.get('number', ""),
        key=f"{key_prefix}_num")
    sub['address'] = ac3.text_input(
        "Адрес", value=sub.get('address', ""),
        key=f"{key_prefix}_adr")
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

    # СПРАВОЧНИКИ: ТТ
    sub['ct_type'] = render_editable_selectbox(
        "Тип ТТ", "TT_TYPE", sub.get(
            'ct_type', ""), f"{key_prefix}_ctt")
    sub['ct_rating'] = render_editable_selectbox(
        "Номинал ТТ", "TT_RATING", sub.get(
            'ct_rating', ""), f"{key_prefix}_ctr")

    sub['meter_type'] = ac3.text_input(
        "Тип ПУ", value=sub.get('meter_type', ""),
        key=f"{key_prefix}_mt")
    return sub


def bus_fields(bus, key_prefix):
    bc1, bc2, bc3 = st.columns([0.6, 0.3, 0.1])
    # СПРАВОЧНИК: ТИП ШИНЫ
    bus['bus_type'] = render_editable_selectbox(
        "Тип шины", "BUS_TYPE", bus.get(
            'bus_type', ""), f"{key_prefix}_bt")
    bus['bus_count'] = bc2.number_input(
        "Кол-во", value=int(bus.get('bus_count', 1)),
        min_value=1, key=f"{key_prefix}_bc")
    return bc3
