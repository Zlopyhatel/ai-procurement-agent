import os
import json
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, text

# Настройка путей до конфига
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "config.json"))


def load_db_url():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    db_folder = config["database"]["folder_name"]
    db_file = config["database"]["file_name"]
    db_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", db_folder, db_file))
    return f"sqlite:///{db_path}"


# Инициализация движка базы данных
DATABASE_URL = load_db_url()
engine = create_engine(DATABASE_URL, echo=False)

st.set_page_config(page_title="Smart Procurement Engine", layout="wide")
st.title("💾 Smart Procurement Engine — Оформление заказа")

# Ограничиваем ввод только цифрами для количества (защита фронтенда)
client_id = st.number_input("Идентификатор клиента (Client ID)", min_value=1, value=1, step=1)
order_date = st.date_input("Дата заказа", value=datetime.now().date())

# Симуляция таблицы ввода позиций
st.subheader("Позиции заказа")
items = []
col1, col2 = st.columns([3, 1])
with col1:
    item_name = st.text_input("Наименование товара (Запрос клиента)")
with col2:
    quantity = st.number_input("Количество", min_value=1, value=1, step=1)

if item_name:
    items.append({"name": item_name, "quantity": quantity})

if st.button("💾 Сохранить заказ"):
    if not items:
        st.warning("Добавьте хотя бы один товар в заказ.")
    else:
        # Контракт JSON, который уходит в order_service
        order_contract = {
            "client_id": int(client_id),
            "order_date": str(order_date),
            "items": items
        }

        # Импортируем сервис сохранения
        from order_service import save_client_order

        if save_client_order(order_contract, engine):
            st.success("JSON-контракт заказа успешно сгенерирован и сохранен в БД!")
            st.json(order_contract)

if st.button("📊 Аналитика цен (Заглушка)"):
    st.info("Модуль ИИ-анализа предложений запущен в демонстрационном режиме.")