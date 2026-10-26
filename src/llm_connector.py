import os
import json
import requests

# Находим путь к config.json в корне проекта относительно текущего файла src/llm_connector.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "config.json"))


def load_ollama_config():
    """Загружает настройки Ollama из конфигурационного файла"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("ollama", {})
    except Exception as e:
        print(f"⚠️ Ошибка загрузки config.json для Ollama: {e}")
        # Безопасный фолбек, если файл не найден
        return {
            "url": "http://localhost:11434/api/generate",
            "model_name": "qwen2.5:7b",
            "timeout_seconds": 90
        }


def match_items_with_catalog(incoming_names: list[str], existing_catalog: list[dict]) -> dict[str, int]:
    if not incoming_names:
        return {}
    if not existing_catalog:
        return {name: None for name in incoming_names}

    # Динамически получаем параметры ИИ из конфига
    ollama_cfg = load_ollama_config()
    ollama_url = ollama_cfg.get("url")
    model_name = ollama_cfg.get("model_name")
    timeout = ollama_cfg.get("timeout_seconds", 90)

    prompt = f"""
    Ты — ИИ-модуль сопоставления товаров (Entity Matching) для Smart Procurement Engine.
    Твоя задача — определить, есть ли новые товары из прайс-листа в нашем существующем каталоге.
    Они могут называться немного по-разному (разный порядок слов, сокращения).

    Существующий каталог товаров нашей системы:
    {json.dumps(existing_catalog, ensure_ascii=False)}

    Новые товары для анализа:
    {json.dumps(incoming_names, ensure_ascii=False)}

    Верни ответ строго в формате JSON-объекта, где:
    Ключ — это точное название нового товара из списка для анализа.
    Значение — целое число (id) найденного товара из существующего каталога. Если совпадений абсолютно точно нет, верни null.

    Не пиши никаких объяснений, преамбул и markdown-разметки. Только чистый JSON.
    """

    try:
        response = requests.post(ollama_url, json={
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }, timeout=timeout)

        if response.status_code == 200:
            result_text = response.json().get("response", "{}")
            return json.loads(result_text)
        else:
            return {name: None for name in incoming_names}
    except Exception as e:
        print(f"❌ Ошибка подключения к Ollama: {e}")
        return {name: None for name in incoming_names}
