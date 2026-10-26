import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, Table

# Подключаем наш ИИ-коннектор
from llm_connector import match_items_with_catalog

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "config.json"))


class RetailerPriceLoader:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.global_config = json.load(f)

        db_folder = self.global_config["database"]["folder_name"]
        db_file = self.global_config["database"]["file_name"]
        pricelists_folder = self.global_config["pricelists"]["folder_name"]

        db_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", db_folder, db_file))
        self.database_url = f"sqlite:///{db_path}"
        self.pricelists_dir = os.path.abspath(os.path.join(CURRENT_DIR, "..", pricelists_folder))

        self.engine = create_engine(self.database_url, echo=False)

    def load_excel_pricelist(self, file_name: str):
        file_configs = self.global_config["pricelists"]["configs"]
        if file_name not in file_configs:
            print(f"❌ Конфигурация для файла '{file_name}' не найдена в config.json")
            return

        file_cfg = file_configs[file_name]
        retailer_name = file_cfg["retailer_name"]
        read_all_sheets = file_cfg["read_all_sheets"]
        skip_sheets = file_cfg["skip_sheets"]
        header_row = file_cfg["header_row"]
        mapping = file_cfg["mapping"]

        file_path = os.path.join(self.pricelists_dir, file_name)
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return

        print(f"📊 Анализ файла: {file_name}...")
        excel_file = pd.ExcelFile(file_path)

        sheets_to_read = excel_file.sheet_names if read_all_sheets else [excel_file.sheet_names[0]]
        sheets_to_read = [sheet for sheet in sheets_to_read if sheet not in skip_sheets]

        combined_df = pd.DataFrame()
        for sheet in sheets_to_read:
            print(f"📖 Чтение вкладки: '{sheet}' (строка заголовка в Excel: {header_row + 1})...")
            df_sheet = pd.read_excel(file_path, sheet_name=sheet, header=header_row)
            df_sheet.columns = [str(col).strip() for col in df_sheet.columns]
            combined_df = pd.concat([combined_df, df_sheet], ignore_index=True)

        sku_col = mapping['sku']
        name_col = mapping['name']
        price_col = mapping['price']

        missing_cols = [col for col in [sku_col, name_col, price_col] if col not in combined_df.columns]
        if missing_cols:
            print(f"\n❌ Ошибка маршрутизации столбцов в Excel! Не найдены: {missing_cols}")
            return

        # 🔍 ИНТРОСПЕКЦИЯ ТАБЛИЦЫ ТОВАРОВ (retailer_item)
        metadata = MetaData()
        try:
            item_table = Table('retailer_item', metadata, autoload_with=self.engine)
            item_cols = [c.name for c in item_table.columns]
            db_name_col = next((c for c in ['name', 'item_name', 'title', 'description'] if c in item_cols), None)

            if not db_name_col:
                print(f"❌ Не удалось определить колонку наименования в 'retailer_item'. Доступные: {item_cols}")
                return
            print(f"🔍 Автодетекция БД: колонка имени в 'retailer_item' -> '{db_name_col}'")
        except Exception as e:
            print(f"❌ Ошибка интроспекции 'retailer_item': {e}")
            return

        # 🔍 ИНТРОСПЕКЦИЯ ТАБЛИЦЫ ИСТОРИИ ЦЕН (retailer_pricelist)
        try:
            price_table = Table('retailer_pricelist', metadata, autoload_with=self.engine)
            price_cols = [c.name for c in price_table.columns]
            # Добавлено 'pricelist_date' в список поиска
            db_date_col = next(
                (c for c in ['change_date', 'pricelist_date', 'created_at', 'date', 'updated_at'] if c in price_cols),
                None)

            if not db_date_col:
                print(f"❌ Не удалось определить колонку даты в 'retailer_pricelist'. Доступные: {price_cols}")
                return
            print(f"🔍 Автодетекция БД: колонка таймстампа в 'retailer_pricelist' -> '{db_date_col}'")
        except Exception as e:
            print(f"❌ Ошибка интроспекции 'retailer_pricelist': {e}")
            return

        # Очистка и фильтрация данных
        combined_df = combined_df.dropna(subset=[sku_col, name_col, price_col])
        combined_df[price_col] = pd.to_numeric(combined_df[price_col], errors='coerce')
        combined_df = combined_df.dropna(subset=[price_col])

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.engine.begin() as connection:
            # Получаем или создаем ритейлера
            retailer_id = connection.execute(
                text("SELECT id FROM retailer WHERE name = :name"), {"name": retailer_name}
            ).scalar()

            if not retailer_id:
                connection.execute(text("INSERT INTO retailer (name) VALUES (:name)"), {"name": retailer_name})
                retailer_id = connection.execute(text("SELECT id FROM retailer WHERE name = :name"),
                                                 {"name": retailer_name}).scalar()

            # Достаем глобальный каталог с учетом динамического имени поля
            catalog_rows = connection.execute(text(f"SELECT id, {db_name_col} FROM retailer_item")).fetchall()
            existing_catalog = [{"id": r, "name": r} for r in catalog_rows]

            incoming_names = combined_df[name_col].astype(str).tolist()
            print("🤖 Отправка уникальных позиций в Qwen 2.5 для сопоставления...")
            ai_matches = match_items_with_catalog(incoming_names, existing_catalog)

            items_inserted = 0
            prices_inserted = 0

            for index, row in combined_df.iterrows():
                raw_sku = row[sku_col]
                sku = str(int(raw_sku)).strip() if isinstance(raw_sku, float) and raw_sku.is_integer() else str(
                    raw_sku).strip()
                name = str(row[name_col]).strip()
                price = float(row[price_col])

                matched_id = ai_matches.get(name)
                if matched_id:
                    item_id = matched_id
                else:
                    try:
                        connection.execute(text(f"""
                            INSERT INTO retailer_item (retailer_sku, {db_name_col})
                            VALUES (:sku, :name)
                            ON CONFLICT(retailer_sku) DO NOTHING
                        """), {"sku": sku, "name": name})
                    except Exception:
                        continue

                    item_id = connection.execute(
                        text("SELECT id FROM retailer_item WHERE retailer_sku = :sku"), {"sku": sku}
                    ).scalar()

                # Динамически подставляем имя колонки даты db_date_col при INSERT
                connection.execute(text(f"""
                    INSERT INTO retailer_pricelist (retailer_item_id, retailer_id, price, {db_date_col})
                    VALUES (:item_id, :retailer_id, :price, :date)
                """), {"item_id": item_id, "retailer_id": retailer_id, "price": price, "date": current_time})

                items_inserted += 1
                prices_inserted += 1

        print(f"🎉 Прайс-лист поставщика '{retailer_name}' успешно импортирован!")
        print(f"📊 Всего обработано строк: {items_inserted}, записано актуальных цен: {prices_inserted}.\n")
