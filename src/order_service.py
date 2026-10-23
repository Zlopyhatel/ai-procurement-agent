from sqlalchemy.orm import Session
from database_orders import sessionLocal, Client, Order, OrderItem


class OrderService:
    def __init__(self):
        # Открываем диспетчер сессий для работы с БД
        self.db: Session = sessionLocal()

    def ensure_test_client_exists(self, client_id: str):
        """
        Проверяет наличие тестового клиента в БД.
        Если клиента нет, создает его с дефолтными данными из ЛК.
        """
        client = self.db.query(Client).filter(Client.client_id == client_id).first()

        if not client:
            print(f"[Order Service] Клиент {client_id} не найден. Создаем профиль из ЛК...")
            new_client = Client(
                client_id=client_id,
                name="ООО Тестовый клиент",
                address="г. Москва, ул. Ленина, д. 10, оф. 42",
                other="Доставка в офис"
            )
            self.db.add(new_client)
            self.db.commit()  # Фиксируем создание клиента
            print(f"[Order Service] Профиль клиента {client_id} успешно добавлен.")

    def save_frontend_order(self, payload: dict) -> int:
        """
        Принимает JSON-контракт с фронтенда, парсит его и сохраняет в БД.
        Возвращает ID созданного заказа.
        """
        try:
            client_id = payload.get("client_id")
            order_date = payload.get("order_date")
            items = payload.get("items", [])

            # 1. Гарантируем, что наш фиксированный клиент существует в базе
            self.ensure_test_client_exists(client_id)

            # 2. Создаем сущность Заказа (procurement_order)
            new_order = Order(
                client_id=client_id,
                order_date=order_date,
                delivery_required=True  # По умолчанию из ЛК требуется доставка
            )
            self.db.add(new_order)

            # Нам нужно сделать flush, чтобы SQLAlchemy получила от БД сгенерированный ID заказа,
            # но еще не закрывала транзакцию окончательно
            self.db.flush()

            print(f"[Order Service] Создан заказ №{new_order.id} на дату {order_date}")

            # 3. Парсим массив товаров и сохраняем каждую позицию (order_item)
            for item in items:
                new_item = OrderItem(
                    order_id=new_order.id,  # Привязываем позицию к нашему созданному заказу
                    good_name=item.get("good_name"),
                    quantity=item.get("quantity")
                )
                self.db.add(new_item)
                print(f" -> Добавлена позиция: {new_item.good_name} ({new_item.quantity} шт.)")

            # 4. Если всё прошло без ошибок, закрываем транзакцию одной командой
            self.db.commit()
            print(f"[Order Service] Заказ №{new_order.id} полностью сохранен в БД.")
            return new_order.id

        except Exception as e:
            # Если на каком-то этапе произошел сбой, откатываем все изменения,
            # чтобы в базе не зависли "половинчатые" данные (грязная запись)
            self.db.rollback()
            print(f"[Order Service] КРИТИЧЕСКАЯ ОШИБКА транзакции: {e}")
            raise e
        finally:
            # В конце обязательно закрываем соединение, возвращая его в пул
            self.db.close()
