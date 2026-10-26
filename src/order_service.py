import json
from sqlalchemy import text, Engine

def save_client_order(order_contract: dict, engine: Engine) -> bool:
    """
    Принимает чистый JSON-контракт заказа и экземпляр engine.
    Раскладывает данные по таблицам procurement_order и client_item.
    """
    client_id = order_contract.get("client_id")
    order_date = order_contract.get("order_date")
    items = order_contract.get("items", [])

    try:
        with engine.begin() as connection:
            # 1. Запись заголовка заказа в procurement_order
            # Поля соответствуют твоей академической singular-схеме
            result = connection.execute(
                text("""
                INSERT INTO procurement_order (client_id, order_date)
                VALUES (:client_id, :order_date)
                RETURNING id
                """),
                {"client_id": client_id, "order_date": order_date}
            )
            order_id = result.scalar()

            # 2. Запись позиций заказа в client_item
            for item in items:
                connection.execute(
                    text("""
                    INSERT INTO client_item (procurement_order_id, name, quantity)
                    VALUES (:order_id, :name, :quantity)
                    """),
                    {"order_id": order_id, "name": item["name"], "quantity": item["quantity"]}
                )
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения контракта заказа в БД: {e}")
        return False