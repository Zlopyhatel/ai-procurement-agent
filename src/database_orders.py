import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Физический путь к нашей объединенной базе данных
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'procurement_orders.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()


# ==========================================
# 👥 КОНТУР КЛИЕНТА & ЗАКАЗОВ (Client Side)
# ==========================================

class Client(base):
    """Таблица: client (Информация о покупателе)"""
    __tablename__ = "client"

    client_id = Column(String, primary_key=True, index=True)  # UniqueID
    name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    other = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order_list = relationship("Order", back_populates="client")


class ClientItem(base):
    """Таблица: client_item (Словарь/история уникальных названий товаров от пользователей)"""
    __tablename__ = "client_item"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID
    order_id = Column(Integer, ForeignKey("procurement_order.id"), nullable=False)
    good_name = Column(String, nullable=False)

    order = relationship("Order", back_populates="client_item_list")


class Order(base):
    """Таблица: procurement_order (Спецификация заказа клиента)"""
    __tablename__ = "procurement_order"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID заказа
    client_id = Column(String, ForeignKey("client.client_id"), nullable=False)  # user_ID со схемы
    item_measure = Column(String, default="pcs")
    quantity = Column(Integer, default=1)
    date = Column(String, nullable=False)
    delivery_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="order_list")
    client_item_list = relationship("ClientItem", back_populates="order")
    mapping_list = relationship("ItemMapping", back_populates="order")


# ==========================================
# 🤖 КОНТУР ИИ-АНАЛИТИКИ & МАТЧИНГА (AI/Core Bridge)
# ==========================================

class ItemMapping(base):
    """Таблица: item_mapping (Результат работы ИИ по связыванию заказа и прайса)"""
    __tablename__ = "item_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID
    order_id = Column(Integer, ForeignKey("procurement_order.id"), nullable=False)  # order_ID со схемы
    retailer_item_id = Column(Integer, ForeignKey("retailer_item.id"), nullable=False)
    date = Column(String, nullable=False)
    client_approve = Column(Boolean, default=False)
    confidence_score = Column(Float, default=1.0)  # Тот самый коэффициент уверенности ИИ

    order = relationship("Order", back_populates="mapping_list")
    retailer_item = relationship("RetailerItem", back_populates="mapping_list")
    best_price_list = relationship("BestPricesList", back_populates="item_mapping")


class BestPricesList(base):
    """Таблица: best_prices_list (Финальные рекомендации лучших цен)"""
    __tablename__ = "best_prices_list"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID
    item_mapping_id = Column(Integer, ForeignKey("item_mapping.id"), nullable=False)
    date = Column(String, nullable=False)
    best_price = Column(Float, nullable=False)
    available_quantity = Column(Integer, default=0)

    item_mapping = relationship("ItemMapping", back_populates="best_price_list")


# ==========================================
# 🏬 КОНТУР ПОСТАВЩИКОВ & ПРАЙСОВ (Vendor Side)
# ==========================================

class RetailerItem(base):
    """Таблица: retailer_item (Глобальный каталог товаров БЕЗ привязки к продавцу)"""
    __tablename__ = "retailer_item"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID
    retailer_sku = Column(String, unique=True, index=True, nullable=False)  # Уникальный артикул
    item_name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    mapping_list = relationship("ItemMapping", back_populates="retailer_item")
    pricelist_entries = relationship("RetailerPricelist", back_populates="retailer_item")


class RetailerPricelist(base):
    """Таблица: retailer_pricelist (Срезы цен поставщиков на конкретные товары)"""
    __tablename__ = "retailer_pricelist"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID
    retailer_item_id = Column(Integer, ForeignKey("retailer_item.id"), nullable=False)
    retailer_id = Column(Integer, ForeignKey("retailer.id"), nullable=False)  # Чей прайс?
    price = Column(Float, nullable=False)
    pricelist_date = Column(String, nullable=False)
    pricelist_status = Column(String, default="active")  # Статус (активен/архив)

    retailer_item = relationship("RetailerItem", back_populates="pricelist_entries")
    retailer = relationship("Retailer", back_populates="pricelist_entries")


class Retailer(base):
    """Таблица: retailer (Справочник поставщиков: Комус, Атташе и т.д.)"""
    __tablename__ = "retailer"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UniqueID
    name = Column(String, unique=True, nullable=False)  # Имя бренда

    pricelist_entries = relationship("RetailerPricelist", back_populates="retailer")


# --- Автоматическая сборка структуры ---
def init_full_database():
    base.metadata.create_all(bind=engine)
    print("[Database Engine] Полная структура БД по новой ERD-схеме успешно развернута в Singular-стандарте.")


if __name__ == "__main__":
    init_full_database()
