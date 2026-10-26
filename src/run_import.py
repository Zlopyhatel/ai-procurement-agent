import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app_loader import RetailerPriceLoader


def main():
    loader = RetailerPriceLoader()

    print("=========================================================================")
    print("📦 Умный импорт Smart Procurement Engine (Боевой режим)")
    print("=========================================================================\n")

    print("Выберите файл из папки 'pricelists' для загрузки в систему:")
    print(" 1. komus_opt_price_7.xlsx (Комус - Оптовый)")
    print(" 2. PRICELIST_ATTACHER.RU.xlsx (Атташе - Многостраничный)")
    print(" 3. SBI-Pr-Kanz.xlsx (Сиббланк издат - Сложная шапка)")

    choice = input("\nВведите номер файла (1, 2 или 3): ").strip()

    if choice == "1":
        file_name = "komus_opt_price_7.xlsx"
    elif choice == "2":
        file_name = "PRICELIST_ATTACHER.RU.xlsx"
    elif choice == "3":
        file_name = "SBI-Pr-Kanz.xlsx"
    else:
        print("❌ Неверный выбор.")
        return

    loader.load_excel_pricelist(file_name)


if __name__ == "__main__":
    main()
