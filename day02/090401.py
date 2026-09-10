import streamlit as st
import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__),"..", "common", "raw_trade_data.csv")
# CSV_PATH = os.path.join(os.path.dirname(__file__), "raw_trade_data.csv")

# 환율 샘플 데이터
# 딕셔너리로 표 만들기

exchange_data = {
    "통화":["USD", "EUR", "JPY(100엔)", "CNY"], 
    "환율(KRW)":[1390.50, 1503.20, 930.80, 191.30], 
    "전일대비":[+5.2, -3.1, +1.0, -0.4]
}
df_exchange = pd.DataFrame(exchange_data)







st.title("💱오늘의환율 대시보드")
st.caption("아래 데이터는 실제 환율이 아닌 실습용 샘플 데이터입니다.")

st.subheader("1) 환율 표 보기")
st.write ("▶ st.dataframe (상호적용 가능한 표)")
st.dataframe(df_exchange, use_container_width=True)

st.write ("▶ st.table (정적인 표)")
st.table(df_exchange)


st.markdown("---")

st.subheader("2) 주요 환율 보기 (st.metric)")

    # st.metric(라벨, 현재값, 증감값)
A1,A2,A3 = st.columns(3)

A1, A2, A3 = st.columns(3)

with A1:
    st.metric(label="USD/KRW", value="1,450.5", delta="+5.2")
with A2:
    st.metric(label="EUR/KRW", value="1,503.2", delta="-3.1")
with A3:
    st.metric(label="JPY(100)/KRW", value="930.8", delta="+1.0")
    
st.markdown("---")

st.subheader("3) 보너스: 무역 원본 데이터 미리보기")
st.write ("공용 데이터 파일 raw_table_data.csv를 읽어 온 상위 5행입니다.")

df_trade_req = pd.read_csv(CSV_PATH, encoding="utf-8")
st.dataframe(df_trade_req.head(5),use_container_width=True)