import streamlit as st


def tp_fields(data=None):
    """Поля характеристик ТП (для форм)"""
    c1, c2, c3 = st.columns(3)
    res = data or {}
    res['address'] = c1.text_input("Адрес ТП", value=res.get('address', ""))
    res['district'] = c1.text_input("Район", value=res.get('district', ""))
    res['region'] = c2.text_input("Округ", value=res.get('region', ""))
    res['voltage'] = c2.selectbox(
        "Напряжение", [
            "10/0.4 кВ", "6/0.4 кВ", "20/0.4 кВ"], index=0)
    res['transformer_type'] = c3.text_input(
        "Тип трансформатора", value=res.get(
            'transformer_type', ""))
    res['uspd_type'] = c3.text_input(
        "Тип УСПД", value=res.get(
            'uspd_type', ""))
    return res


def subscriber_fields(sub, key_prefix):
    """Все поля абонента (для форм)"""
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

    sub['ct_type'] = ac1.text_input(
        "Тип ТТ", value=sub.get('ct_type', ""),
        key=f"{key_prefix}_ctt")
    sub['ct_rating'] = ac2.text_input(
        "Номинал ТТ", value=sub.get(
            'ct_rating', ""), key=f"{key_prefix}_ctr")
    sub['meter_type'] = ac3.text_input(
        "Тип ПУ", value=sub.get('meter_type', ""),
        key=f"{key_prefix}_mt")
    return sub
