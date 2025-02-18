import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title='Финансы и Чаевые', layout='wide')

st.sidebar.header('Настройки приложения')
st.title('\U0001F4C8 Котировки акций Apple (AAPL)')

period = st.sidebar.selectbox('Выберите период:', ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'], index=4)

stock = yf.Ticker('AAPL')
data = stock.history(period=period)

if data.empty:
    st.warning('Нет данных за выбранный период.')
else:
    st.line_chart(data[['Close']])
    
    csv_data = data.to_csv(index=True)
    st.download_button(label='Скачать CSV', data=csv_data, file_name='apple_stock.csv', mime='text/csv')

st.title('\U0001F4B0 Анализ чаевых (Tips)')

def load_data():
    uploaded_file = st.sidebar.file_uploader('Загрузите CSV-файл с чаевыми', type=['csv'])
    if uploaded_file:
        return pd.read_csv(uploaded_file)
    return None

tips_df = load_data()

if tips_df is not None:
    st.write('Данные загружены:')
    st.dataframe(tips_df.head())

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
    st.download_button(label='Скачать график', data=img_buf.getvalue(), file_name='tips_analysis.png', mime='image/png')