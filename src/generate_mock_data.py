import os
import sys
import random
import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка путей для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import database_orders
except ImportError:
    database_orders = None

# Путь к БД
DB_PATH = os.path.abspath(os.path.join(current_dir, "..", "data", "procurement_orders.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Единая фабрика сессий для скрипта и тестов
_engine = create_engine(DATABASE_URL, echo=False)
_Session = sessionmaker(bind=_engine)


def generate_mock_data():
    print("🚀 Инициализация структуры базы данных из моделей...")

    if database_orders and hasattr(database_orders, 'base'):
        database_orders.base.metadata.create_all(_engine)
        print("✅ Структура таблиц успешно проверена через database_orders.base.")
    else:
        print("⚠️ Модуль моделей не найден, таблицы должны быть созданы заранее.")

    session = _Session()
    print("🚀 Запуск генерации тестовых данных для Smart Procurement Engine...")

    try:
        # 1. Наполнение таблицы: retailer
        retailers_data = [
            {"id": 1, "name": "Комус"},
            {"id": 2, "name": "Атташе"}
        ]

        for r in retailers_data:
            session.execute(
                text("""
                     INSERT
                     OR IGNORE INTO retailer (id, name) 
                VALUES (:id, :name)
                     """), r
            )
        print("✅ Таблица 'retailer' заполнена (Комус, Атташе).")

        # 2. Наполнение таблицы: retailer_item
        items_data = [
            {"retailer_sku": "PAPER-A4-80-01", "name": "Бумага А4 СветоКопи (SvetoCopy), 80г/м2, 500л",
             "category": "Бумага"},
            {"retailer_sku": "PAPER-A4-80-02", "name": "Бумага А4 Снегурочка, 80г/м2, 500л", "category": "Бумага"},
            {"retailer_sku": "NOTE-A5-96-01", "name": "Тетрадь А5 в клетку, 96 листов, жесткая обложка",
             "category": "Бумажная продукция"},
            {"retailer_sku": "STICK-76-76-01", "name": "Блок бумажный с клейким краем 76х76 мм, 100л, желтый",
             "category": "Бумажная продукция"},
            {"retailer_sku": "PEN-BALL-BLUE-01", "name": "Ручка шариковая ErichKrause Ultra Glide, синяя",
             "category": "Пишущие принадлежности"},
            {"retailer_sku": "PEN-GEL-BLACK-01", "name": "Ручка гелевая Pilot G-1, 0.7 мм, черная",
             "category": "Пишущие принадлежности"},
            {"retailer_sku": "PENCIL-HB-01", "name": "Карандаш чернографитный Koh-I-Noor 1500 HB с ластиком",
             "category": "Пишущие принадлежности"},
            {"retailer_sku": "MARKER-TEXT-01", "name": "Набор текстовыделителей Stabilo Boss (4 цвета)",
             "category": "Пишущие принадлежности"},
            {"retailer_sku": "FOLDER-ARC-75-01", "name": "Папка-регистратор Attache 75мм, мрамор/черная",
             "category": "Папки и архивация"},
            {"retailer_sku": "CLIP-25-01", "name": "Зажимы для бумаг 25 мм, в упаковке 12 шт",
             "category": "Офисные мелочи"},
            {"retailer_sku": "STAPLER-24-01", "name": "Степлер Brauberg до 20 листов, №24/6",
             "category": "Офисные мелочи"},
            {"retailer_sku": "SCISSORS-18-01", "name": "Ножницы офисные 18 см, асимметричные ручки",
             "category": "Офисные мелочи"}
        ]

        for item in items_data:
            session.execute(
                text("""
                     INSERT
                     OR IGNORE INTO retailer_item (retailer_sku, name, category) 
                VALUES (:retailer_sku, :name, :category)
                     """), item
            )
        print(f"✅ Таблица 'retailer_item' заполнена ({len(items_data)} позиций).")

        # Получаем ID из базы
        db_items = session.execute(text("SELECT id, retailer_sku FROM retailer_item")).fetchall()

        # 3. Наполнение таблицы: retailer_pricelist (История цен)
        today = datetime.now()
        price_records_count = 0

        for item_row in db_items:
            item_id = item_row
            sku = item_row

            if "PAPER" in sku:
                base_price = 320.0
            elif "PEN" in sku or "PENCIL" in sku:
                base_price = 45.0
            elif "MARKER" in sku or "NOTE" in sku:
                base_price = 180.0
            elif "FOLDER" in sku or "STAPLER" in sku:
                base_price = 250.0
            else:
                base_price = 80.0

            for retailer_id in (1, 2):
                vendor_modifier = 1.05 if (retailer_id == 1 and "PAPER" in sku) else 0.98

                for days_ago in range(3, -1, -1):
                    date_str = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                    daily_flux = random.uniform(-0.03, 0.03)
                    final_price = round(base_price * vendor_modifier * (1 + daily_flux), 2)

                    session.execute(
                        text("""
                             INSERT
                             OR IGNORE INTO retailer_pricelist (retailer_item_id, retailer_id, price, change_date)
                        VALUES (:retailer_item_id, :retailer_id, :price, :change_date)
                             """),
                        {
                            "retailer_item_id": item_id,
                            "retailer_id": retailer_id,
                            "price": final_price,
                            "change_date": date_str
                        }
                    )
                    price_records_count += 1

        print(f"✅ Таблица 'retailer_pricelist' заполнена ({price_records_count} записей цен).")

        # 4. Наполнение таблицы: client (Синхронизировано: БЕЗ поля status)
        session.execute(
            text("""
                 INSERT
                 OR IGNORE INTO client (id, name, inn)
            VALUES (1, 'ООО Вектор Финанс', '7701020304')
                 """)
        )
        print("✅ Таблица 'client' инициализирована дефолтным контрагентом.")

        session.commit()
        print("🎉 База данных успешно наполнена тестовыми данными!")

    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при генерации моков: {e}")
        raise e
    finally:
        session.close()


# =====================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# =====================================================================
class TestProcurementMockData(unittest.TestCase):
    def setUp(self):
        # Открываем чистую сессию для каждого теста, чтобы видеть закоммиченные данные
        self.session = _Session()

    def tearDown(self):
        self.session.close()

    def test_retailers_exist(self):
        """Проверяем, что поставщики Комус и Атташе успешно создались"""
        result = self.session.execute(text("SELECT id, name FROM retailer ORDER BY id")).fetchall()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], "Комус")
        self.assertEqual(result[1][1], "Атташе")

    def test_items_count(self):
        """Проверяем, что все 12 базовых канцтоваров находятся в каталоге"""
        count = self.session.execute(text("SELECT COUNT(*) FROM retailer_item")).scalar()
        self.assertEqual(count, 12)

    def test_pricelist_history_depth(self):
        """Проверяем, что для каждого товара посчиталась история цен"""
        count = self.session.execute(text("SELECT COUNT(*) FROM retailer_pricelist")).scalar()
        self.assertGreaterEqual(count, 96)

    def test_client_stub(self):
        """Проверяем контрагента (Синхронизировано: БЕЗ status)"""
        client = self.session.execute(text("SELECT name, inn FROM client WHERE id = 1")).fetchone()
        self.assertIsNotNone(client)
        self.assertEqual(client[0], "ООО Вектор Финанс")
        self.assertEqual(client[1], "7701020304")


if __name__ == "__main__":
    # 1. Запуск генерации данных
    generate_mock_data()

    # 2. Автоматический запуск тестов для проверки результатов
    print("\n🧪 Запуск встроенных тестов верификации данных...")
    unittest.main(argv=[sys.argv[0]], exit=False)