import os
import pandas as pd

# Создаем папку data в корне проекта, если её ещё нет
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)

# Базовый набор товаров для генерации грязных данных
# Идея: один и тот же товар в разных магазинах называется по-разному
products_data = {
    "market_a": [
        {"vendor_title": "Milk 'Prostokvashino' ultra-past. 3.2% 950ml", "sku": "MK-001", "base_price": 110, "discount_price": 89, "stock_quantity": 45},
        {"vendor_title": "Coffee Lavazza Oro ground 250g", "sku": "CF-102", "base_price": 550, "discount_price": 499, "stock_quantity": 12},
        {"vendor_title": "Paper SvetoCopy Classic A4 500 sheets", "sku": "PR-551", "base_price": 450, "discount_price": 420, "stock_quantity": 150},
        {"vendor_title": "Sugar white crystalline 1kg pack", "sku": "SG-009", "base_price": 75, "discount_price": 75, "stock_quantity": 80}
    ],
    "market_b": [
        {"vendor_title": "Prostokvashino Milk 3,2% 0.95L", "sku": "987234", "base_price": 105, "discount_price": 92, "stock_quantity": 20},
        {"vendor_title": "Lavazza Qualita Oro Coffee 250 grams", "sku": "543112", "base_price": 580, "discount_price": 470, "stock_quantity": 5},
        {"vendor_title": "Svetocopy A4 Printer Paper (500sh)", "sku": "112233", "base_price": 440, "discount_price": 435, "stock_quantity": 200},
        {"vendor_title": "Refined Sugar 1000g", "sku": "665544", "base_price": 78, "discount_price": 69, "stock_quantity": 15}
    ],
    "market_c": [
        {"vendor_title": "Milk Prostokvashino 3.2% 1000ml", "sku": "A-9921", "base_price": 115, "discount_price": 115, "stock_quantity": 10},
        {"vendor_title": "Coffee Lavazza Oro vacuum pack 0.25kg", "sku": "B-4412", "base_price": 600, "discount_price": 520, "stock_quantity": 30},
        {"vendor_title": "Office Paper SvetoCopy A4/500sh", "sku": "C-1109", "base_price": 460, "discount_price": 399, "stock_quantity": 10},
        {"vendor_title": "Crystalline White Sugar 1 kg", "sku": "D-8831", "base_price": 72, "discount_price": 72, "stock_quantity": 120}
    ]
}

def generate_files():
    for market_name, items in products_data.items():
        df = pd.DataFrame(items)
        file_path = os.path.join(data_dir, f"{market_name}_prices.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"Successfully generated database for: {market_name} -> data/{market_name}_prices.csv")

if __name__ == "__main__":
    generate_files()
