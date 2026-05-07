import requests
import streamlit as st

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
API_URL = "http://127.0.0.1:8000"

st.title("⚙️ Управление справочниками")

# Соответствие красивых названий техническим категориям в БД
categories = {
    "Типы УСПД": "USPD",
    "Типы ТТ": "TT_TYPE",
    "Номиналы ТТ": "TT_RATING",
    "Типы шин": "BUS_TYPE",
    "Типы счетчиков": "PU_TYPE",
    "Панели": "PANEL",
    "Тип сборки": "ASSEMBLY",
}

# Выбор категории
selected_label = st.selectbox(
    "Выберите категорию для редактирования", list(
        categories.keys()))
cat_key = categories[selected_label]

st.divider()

# --- БЛОК ДОБАВЛЕНИЯ ---
st.subheader(f"Добавить в: {selected_label}")
with st.form("add_ref_form", clear_on_submit=True):
    new_value = st.text_input("Введите новое значение")
    submitted = st.form_submit_button("➕ Добавить в базу")

    if submitted and new_value:
        res = requests.post(
            f"{API_URL}/refs/",
            json={
                "category": cat_key,
                "value": new_value})
        if res.status_code == 200:
            st.success(f"'{new_value}' добавлено")
            st.rerun()
        else:
            st.error("Ошибка при добавлении (возможно, такое значение уже есть)")

st.divider()

# --- БЛОК ОТОБРАЖЕНИЯ И УДАЛЕНИЯ ---
st.subheader(f"Текущие значения ({selected_label})")

try:
    # Запрашиваем список строк из твоего роутера
    response = requests.get(f"{API_URL}/refs/{cat_key}")
    if response.status_code == 200:
        items = response.json()

        if not items:
            st.info("В этом справочнике пока нет данных")
        else:
            # Выводим каждое значение с кнопкой удаления
            for item_val in items:
                col1, col2 = st.columns([0.85, 0.15])
                col1.write(f"🔹 {item_val}")

                # Чтобы удалять, нам нужно передать ID, но роутер возвращает строки.
                # Если твой роутер возвращает только строки, удаление сделаем
                # по значению.
                if col2.button("🗑️", key=f"del_{cat_key}_{item_val}"):
                    # Здесь предполагается, что в роутере есть удаление по значению или ID
                    # Для примера удаляем по значению (нужно проверить эндпоинт
                    # в refs.py)
                    del_res = requests.delete(
                        f"{API_URL}/refs/{cat_key}/{item_val}")
                    if del_res.status_code == 200:
                        st.rerun()
    else:
        st.error("Не удалось загрузить данные")
except Exception as e:
    st.error(f"Ошибка связи с сервером: {e}")
