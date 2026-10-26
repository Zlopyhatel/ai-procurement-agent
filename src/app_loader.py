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

        # Нормализуем имена колонок: убираем лишние пробелы по краям
        df_sheet.columns = [str(col).strip() for col in df_sheet.columns]
        combined_df = pd.concat([combined_df, df_sheet], ignore_index=True)

    sku_col = mapping['sku']
    name_col = mapping['name']
    price_col = mapping['price']

    # Проверяем наличие колонок с выводом подробной диагностики
    missing_cols = []
    for col in [sku_col, name_col, price_col]:
        if col not in combined_df.columns:
            missing_cols.append(col)

    if missing_cols:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА МАРШРУТИЗАЦИИ СТОЛБЦОВ!")
        print(f"Не удалось найти целевые колонки: {missing_cols}")
        print(f"ℹ️ Реальные первые 10 колонок, обнаруженные на {header_row + 1}-й строке Excel:")
        for idx, real_col in enumerate(list(combined_df.columns)[:10]):
            print(f"  [{idx}] -> '{real_col}'")
        print("\n📋 Содержимое первых 3 строк прочитанной таблицы для анализа:")
        print(combined_df.head(3).to_string())
        return

    # Отсекаем пустые строки
    combined_df = combined_df.dropna(subset=[sku_col, name_col, price_col])
    combined_df[price_col] = pd.to_numeric(combined_df[price_col], errors='coerce')
    combined_df = combined_df.dropna(subset=[price_col])

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with self.engine.begin() as connection:
        retailer_id = connection.execute(
            text("SELECT id FROM retailer WHERE name = :name"), {"name": retailer_name}
        ).scalar()

        if not retailer_id:
            connection.execute(text("INSERT INTO retailer (name) VALUES (:name)"), {"name": retailer_name})
            retailer_id = connection.execute(text("SELECT id FROM retailer WHERE name = :name"), {"name": retailer_name}).scalar()

        catalog_rows = connection.execute(text("SELECT id, name FROM retailer_item")).fetchall()
        existing_catalog = [{"id": r[0], "name": r[1]} for r in catalog_rows]

        incoming_names = combined_df[name_col].astype(str).tolist()
        print("Ollama: Запуск сопоставления позиций (Entity Matching) через Qwen 2.5...")
        ai_matches = match_items_with_catalog(incoming_names, existing_catalog)

        items_inserted = 0
        prices_inserted = 0

        for index, row in combined_df.iterrows():
            sku = str(row[sku_col]).strip()
            name = str(row[name_col]).strip()
            price = float(row[price_col])

            matched_id = ai_matches.get(name)
            if matched_id:
                item_id = matched_id
            else:
                connection.execute(text("""
                    INSERT OR IGNORE INTO retailer_item (retailer_sku, name)
                    VALUES (:sku, :name)
                """), {"sku": sku, "name": name})

                item_id = connection.execute(
                    text("SELECT id FROM retailer_item WHERE retailer_sku = :sku"), {"sku": sku}
                ).scalar()

            connection.execute(text("""
                INSERT INTO retailer_pricelist (retailer_item_id, retailer_id, price, change_date)
                VALUES (:item_id, :retailer_id, :price, :date)
            """), {"item_id": item_id, "retailer_id": retailer_id, "price": price, "date": current_time})

            items_inserted += 1
            prices_inserted += 1

    print(f"🎉 Прайс-лист поставщика '{retailer_name}' успешно импортирован!")
    print(f"📊 Всего обработано строк: {items_inserted}, записано актуальных цен: {prices_inserted}.\n")