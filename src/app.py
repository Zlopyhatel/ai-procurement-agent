import streamlit as st
import datetime

# Инициализация сессионного состояния для динамических строк
if "input_rows" not in st.session_state:
    st.session_state.input_rows = 1

# === НАСТРОЙКА ИНТЕРФЕЙСА ===
st.set_page_config(page_title="Procurement Assistant", page_icon="📝", layout="wide")

# Заголовок
st.markdown("### 🛒 Добавьте товары и укажите требуемое количество")

# Поля метаданных
col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    client_id = st.text_input("Идентификатор клиента (Client ID):", value="CLIENT-777-XYZ")
with col_meta2:
    order_date = st.date_input("Дата заказа:", value=datetime.date.today())

st.write("")  # Отступ

# Сбор элементов формы
items_to_parse = []

for i in range(st.session_state.input_rows):
    row_id = i + 1
    # АДАПТИВНАЯ ВЕРСТКА СТРОКИ: Отдаем 85% ширины под текст и 15% под количество
    c1, c2 = st.columns([0.85, 0.15])

    with c1:
        good_name = st.text_input(
            f"Наименование товара {row_id}:",
            placeholder="Введите тут наименование товара (например: Бумага Svetocopy А4)",
            key=f"name_{row_id}"
        )
    with c2:
        quantity = st.number_input(
            "Кол-во:",
            min_value=1,
            value=1,
            step=1,
            key=f"qty_{row_id}"
        )

    if good_name.strip():
        items_to_parse.append({
            "good_name": good_name.strip(),
            "quantity": quantity
        })

# АДАПТИВНАЯ ВЕРСТКА КНОПОК: Выделяем под кнопки очень узкие колонки,
# а остальную ширину (80%) оставляем пустой справа. Текст больше не сожмется.
c_btn1, c_btn2, _ = st.columns([0.1, 0.1, 0.8])
with c_btn1:
    if st.button("➕ Добавить", use_container_width=True):
        st.session_state.input_rows += 1
        st.rerun()
with c_btn2:
    if st.button("❌ Удалить", use_container_width=True):
        if st.session_state.input_rows > 1:
            st.session_state.input_rows -= 1
            st.rerun()

st.markdown("---")

# Красная кнопка действия
start_button = st.button("📌 Найти лучшие цены у продавцов", type="primary")

st.markdown("### 📊 Мы нашли лучшие цены у продавцов:")

# Логика нажатия
if start_button:
    if not items_to_parse:
        st.warning("⚠️ Не заполнено ни одного наименования товара!")
    else:
        output_payload = {
            "client_id": client_id,
            "order_date": str(order_date),
            "items": items_to_parse
        }
        st.json(output_payload)
