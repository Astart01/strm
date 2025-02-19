import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from io import BytesIO


API_KEY = "U531V46ABDTXSHEV"

st.set_page_config(page_title='Финансы и Чаевые', layout='wide')

st.sidebar.header('Настройки приложения')
st.title('📈 Котировки акций Apple (AAPL)')

period_options = {
    '1d': 'TIME_SERIES_INTRADAY',
    '5d': 'TIME_SERIES_DAILY',
    '1mo': 'TIME_SERIES_DAILY',
    '3mo': 'TIME_SERIES_DAILY',
    '6mo': 'TIME_SERIES_DAILY',
    '1y': 'TIME_SERIES_DAILY',
    '2y': 'TIME_SERIES_DAILY',
    '5y': 'TIME_SERIES_DAILY',
    '10y': 'TIME_SERIES_DAILY'
}

period = st.sidebar.selectbox('Выберите период:', list(period_options.keys()), index=1)


def get_stock_data(symbol="AAPL", period="1d"):
    try:
        function = period_options[period]
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={API_KEY}&outputsize=compact"

        response = requests.get(url)
        data = response.json()

        if "Error Message" in data:
            st.error("❌ Ошибка при получении данных. Проверьте API-ключ или попробуйте позже.")
            return None

        if period == '1d':
            timeseries = data.get("Time Series (5min)", {})
        else:
            timeseries = data.get("Time Series (Daily)", {})

        if not timeseries:
            st.warning("⚠️ Данные отсутствуют. Попробуйте выбрать другой период.")
            return None

        df = pd.DataFrame.from_dict(timeseries, orient='index', dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df

    except Exception as e:
        st.error(f"🚨 Ошибка: {e}")
        return None


data = get_stock_data(period=period)

if data is not None:
    st.write("📊 Загруженные данные:")
    st.write(data.head(10))  # Вывести первые 10 строк данных

    # 🔹 График цен (Open, High, Low, Close)
    st.subheader("📈 Динамика цен AAPL")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data['1. open'], label="Open", linestyle="--")
    ax.plot(data.index, data['2. high'], label="High", linestyle="-")
    ax.plot(data.index, data['3. low'], label="Low", linestyle="-")
    ax.plot(data.index, data['4. close'], label="Close", linestyle="-", linewidth=2)

    ax.set_xlabel("Дата")
    ax.set_ylabel("Цена ($)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # 🔹 График объёма торгов
    st.subheader("📊 Объём торгов (Volume)")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(data.index, data['5. volume'], color='skyblue', label="Объём торгов")

    ax.set_xlabel("Дата")
    ax.set_ylabel("Объём")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    csv_data = data.to_csv(index=True)
    st.download_button(label='📥 Скачать CSV', data=csv_data, file_name='apple_stock.csv', mime='text/csv')

else:
    st.warning("⚠️ Данные временно недоступны. Попробуйте позже.")


st.title('💰 Анализ чаевых (Tips)')

def load_data():
    uploaded_file = st.sidebar.file_uploader('Загрузите CSV-файл с чаевыми', type=['csv'])
    if uploaded_file:
        return pd.read_csv(uploaded_file)
    return None

tips_df = load_data()

if tips_df is not None:
    st.write('✅ Данные загружены:')
    st.dataframe(tips_df.head(10))

    st.subheader('1️⃣ График зависимости чаевых от суммы заказа')
    fig, ax = plt.subplots()
    sns.scatterplot(x=tips_df['total_bill'], y=tips_df['tip'], hue=tips_df['smoker'], ax=ax)
    st.pyplot(fig)

    st.subheader('2️⃣ Распределение чаевых')
    fig, ax = plt.subplots()
    sns.histplot(tips_df['tip'], bins=20, kde=True, ax=ax)
    st.pyplot(fig)

    st.subheader('3️⃣ Чаевые по дням недели')
    fig, ax = plt.subplots()
    sns.boxplot(x=tips_df['day'], y=tips_df['tip'], hue=tips_df['sex'], ax=ax)
    st.pyplot(fig)

    st.subheader("📊 Корреляция между переменными")

    numeric_tips = tips_df.select_dtypes(include=['number'])
    categorical_columns = ['sex', 'smoker', 'day', 'time']
    tips_encoded = pd.get_dummies(tips_df, columns=categorical_columns, drop_first=True)
    final_tips = pd.concat([numeric_tips, tips_encoded], axis=1)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(final_tips.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    st.subheader('5️⃣ Средний размер чаевых по дням недели')
    avg_tips = tips_df.groupby('day')['tip'].mean().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(x='day', y='tip', data=avg_tips, ax=ax)
    st.pyplot(fig)

    img_buf = BytesIO()
    fig.savefig(img_buf, format='png')
    st.download_button(label='📥 Скачать график', data=img_buf.getvalue(), file_name='tips_analysis.png', mime='image/png')