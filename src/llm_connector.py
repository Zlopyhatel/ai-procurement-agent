import json


class LLMConnector:
    def __init__(self):
        # Здесь в будущем мы инициализируем подключение к API (OpenAI / Ollama)
        pass

    def validate_and_clean_text(self, raw_text: str) -> str:
        """
        Базовый ФЛК (Форматно-логический контроль) текста.
        Очищает строку от лишних пробелов и проверяет, что запрос не пустой.
        """
        if not raw_text or len(raw_text.strip()) < 5:
            raise ValueError("The request text is too short or empty. Please specify what you want to buy.")

        return raw_text.strip()

    def get_mock_ai_parsing(self, cleaned_text: str) -> list:
        """
        Временный метод-заглушка (Mock), который имитирует то, что вернет нам ИИ.
        Показывает, к какой структуре данных (JSON/List) мы стремимся.
        """
        print(f"[LLM Connector] Received text for parsing: {cleaned_text}")

        # Симулируем работу ИИ: он распознал в тексте бумагу и молоко
        mock_parsed_items = [
            {
                "good_name": "SvetoCopy A4 paper",
                "quantity": 2,
                "required_unit": "pack",
                "max_price": None  # ИИ не нашел жесткого ограничения по цене на этот товар
            },
            {
                "good_name": "milk 3.2%",
                "quantity": 3,
                "required_unit": "liter",
                "max_price": None
            }
        ]

        return mock_parsed_items