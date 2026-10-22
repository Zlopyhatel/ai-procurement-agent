import streamlit as st
import pandas as pd
import os
# Импортируем наш новый коннектор
from llm_connector import LLMConnector

st.set_page_config(
    page_title="Smart Procurement Engine",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Smart Procurement Engine")
st.subheader("AI-Powered Price Monitor & Sourcing Assistant")
st.markdown("---")

col1, col2 = st.columns()

with col1:
    st.header("📋 Procurement Request")

    user_query = st.text_area(
        label="What do you need to buy? (Enter in plain English):",
        value="Need to buy 2 packs of SvetoCopy A4 paper and 3 liters of milk. Budget is $15 total.",
        height=150
    )

    start_button = st.button("🚀 Find Best Prices", type="primary")

with col2:
    st.header("📊 Market Offers & Analysis")

    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    tab1, tab2, tab3 = st.tabs(["Market A (Metro)", "Market B (Auchan)", "Market C (Lenta)"])

    try:
        with tab1:
            st.dataframe(pd.read_csv(os.path.join(data_dir, "market_a_prices.csv")), use_container_width=True)
        with tab2:
            st.dataframe(pd.read_csv(os.path.join(data_dir, "market_b_prices.csv")), use_container_width=True)
        with tab3:
            st.dataframe(pd.read_csv(os.path.join(data_dir, "market_c_prices.csv")), use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Mock data files not found.")

    st.markdown("---")
    st.subheader("🤖 AI Sourcing Recommendation")

    if start_button:
        st.info(f"Processing query: *\"{user_query}\"*")

        # Инициализируем коннектор и запускаем цепочку обработки текста
        llm = LLMConnector()
        try:
            # 1. Валидируем и чистим текст
            cleaned_text = llm.validate_and_clean_text(user_query)

            # 2. Получаем структурированный список товаров (пока мок)
            parsed_items = llm.get_mock_ai_parsing(cleaned_text)

            # Отображаем пользователю, как система "увидела" его запрос
            st.success("Text successfully parsed by UI controller!")
            st.write("### Extracted Items Schema (JSON):")
            st.json(parsed_items)

        except ValueError as e:
            st.error(f"Validation Error: {e}")
    else:
        st.write("Click the button on the left to simulate the procurement matching process.")