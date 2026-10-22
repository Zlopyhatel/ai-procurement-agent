import streamlit as pd_st  # используем алиас, чтобы не путать с pandas
import streamlit as st
import pandas as pd
import os

# Настройка страницы браузера
st.set_page_config(
    page_title="Smart Procurement Engine",
    page_icon="🛍️",
    layout="wide"
)

# Заголовок приложения
st.title("🛍️ Smart Procurement Engine")
st.subheader("AI-Powered Price Monitor & Sourcing Assistant")
st.markdown("---")

# Создаем две колонки: левая для ввода, правая для результатов
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Procurement Request")

    # Текстовое поле для свободного ввода пользователя (наш будущий ИИ-вход)
    user_query = st.text_area(
        label="What do you need to buy? (Enter in plain English):",
        value="Need to buy 2 packs of SvetoCopy A4 paper and 3 liters of milk. Budget is $15 total.",
        height=150
    )

    # Кнопка запуска процесса
    start_button = st.button("🚀 Find Best Prices", type="primary")

with col2:
    st.header("📊 Market Offers & Analysis")

    # Путь к нашей папке с мок-данными
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Вкладки для просмотра загруженных прайс-листов ритейлеров
    tab1, tab2, tab3 = st.tabs(["Market A (Metro)", "Market B (Auchan)", "Market C (Lenta)"])

    try:
        with tab1:
            df_a = pd.read_csv(os.path.join(data_dir, "market_a_prices.csv"))
            st.dataframe(df_a, use_container_width=True)

        with tab2:
            df_b = pd.read_csv(os.path.join(data_dir, "market_b_prices.csv"))
            st.dataframe(df_b, use_container_width=True)

        with tab3:
            df_c = pd.read_csv(os.path.join(data_dir, "market_c_prices.csv"))
            st.dataframe(df_c, use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Mock data files not found. Please run generate_mock_data.py first.")

    # Область для вывода рекомендаций (пока заглушка)
    st.markdown("---")
    st.subheader("🤖 AI Sourcing Recommendation")

    if start_button:
        st.info(f"Processing query: *\"{user_query}\"*")
        st.success("UI Skeleton works perfectly! Next step: hook up the LLM parsing backend.")
    else:
        st.write("Click the button on the left to simulate the procurement matching process.")
