import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Настройки путей к изолированному файлу базы данных
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'procurement_orders.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()


# --- СУЩНОСТЬ 1: КЛИЕНТ (Client) ---
class Client(base):
    __tablename__ = "client"

    client_id = Column(String, primary_key=True, index=True)  # ИД клиента с экрана
    name = Column(String, nullable=True)  # Имя (из ЛК)
    address = Column(String, nullable=True)  # Адрес (из ЛК)
    other = Column(String, nullable=True)  # Заметки
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь переименована в единственное число + тип сущности (order_list)
    order_list = relationship("Order", back_populates="client")


# --- СУЩНОСТЬ 2: ЗАКАЗ (Order) ---
class Order(base):
    __tablename__ = "procurement_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, ForeignKey("client.client_id"), nullable=False)
    order_date = Column(String, nullable=False)  # Дата с экрана
    delivery_required = Column(Boolean, default=True)  # Нужна ли доставка (из ЛК)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="order_list")
    # Связь переименована в единственное число + тип сущности (item_list)
    item_list = relationship("OrderItem", back_populates="order")


# --- СУЩНОСТЬ 3: ПОЗИЦИЯ ЗАКАЗА (OrderItem) ---
class OrderItem(base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("procurement_order.id"), nullable=False)
    good_name = Column(String, nullable=False)  # Товар с экрана
    quantity = Column(Integer, nullable=False)  # Кол-во с экрана

    order = relationship("Order", back_populates="item_list")


# Функция автоматического создания таблиц (DDL)
def init_orders_db():
    base.metadata.create_all(bind=engine)
    print("[Database Orders] Database created successfully.")


if __name__ == "__main__":
    init_orders_db()