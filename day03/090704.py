"""
k-drama 데이터 필터링, 결측치 정리
Number of Episode 필터링
넷플릭스, tvn으로 필터링
kdrama_cleaned.csv 로 저장
실행방법 : streamlit run 090704.py
"""

import pandas as pd
import streamlit as st

st.title("📺 K-드라마 데이터 필터링 & 결측치 정리")
st.caption("에피소드, OTT 조건으로 필터링해보고, 결측치를 제거해서 새 csv로 저장합니다.")

CSV_PATH = "kdrama.csv"

try: 
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    st.error("kdrama.csv 파일을 찾을 수 없습니다.")
else: 
    st.metric("원본 데이터 행 개수", f"{len(df)}행")

    st.markdown("---")
    
    # 0) 결측치 확인 및 정리 (Number of Episode 컬럼 기준)
    st.subheader("0) 결측치 확인 및 정리")
    missing_episode_count = df["Number of Episode"].isna().sum()
    st.write(f"Number of Episode 열의 결측치 개수: **{missing_episode_count}개**")

    df_cleaned = df.dropna(subset=['Number of Episode'])
    st.write(f"결측치 제거 후 데이터 : **{len(df_cleaned)}행**")
    
    st.markdown("---")

    # 1) Number of Episode 10개 이상으로 필터링
    st.subheader("1) 에피소드 10개 이상 드라마")
    over_10 = df_cleaned[df_cleaned["Number of Episode"] >= 10]
    
    st.write(f"에피소드 10개 이상 드라마 : **{len(over_10)}개**")
    st.dataframe(over_10[["Name", "Number of Episode", "Network"]].head(), use_container_width=False)
    
    st.markdown("---")
    
    # 2) 넷플릭스, 티비엔 필터링
    st.subheader("2) OTT 필터링 결과")
    # Network 컬럼에 공백이나 여러 채널이 섞여 있을 수 있으므로 str.contains를 사용합니다.
    Netflix_df = df_cleaned[df_cleaned["Network"].str.contains("Netflix", na=False)]
    tvN_df = df_cleaned[df_cleaned["Network"].str.contains("tvN", na=False)] 

    col1, col2 = st.columns(2)
    with col1:
        st.metric("넷플릭스", f"{len(Netflix_df)}개")
    with col2:
        st.metric("티비엔", f"{len(tvN_df)}개")

    st.markdown("---")

    # 3) 두 조건을 동시에 만족하는 행(10개 에피소드 이상 & 넷플릭스)
    st.subheader("3) 10개 에피소드 이상 넷플릭스 드라마")
    over_10_Netflix = df_cleaned[(df_cleaned["Number of Episode"] >= 10) & (df_cleaned["Network"].str.contains("Netflix", na=False))]
    
    st.write(f"10개 에피소드 이상 넷플릭스 드라마 : **{len(over_10_Netflix)}개**")
    st.dataframe(over_10_Netflix[["Name", "Number of Episode", "Network"]].head(), use_container_width=False)

    st.markdown("---")

    # 4) 데이터 저장 기능
    st.subheader("4) 정제된 데이터 저장")
    st.write("결측치를 처리한 데이터를 csv 파일로 저장합니다.")
    
    if st.button("kdrama_cleaned.csv 저장하기"):
        output_path = "kdrama_cleaned.csv"
        df_cleaned.to_csv(output_path, index=False)
        st.success("✨ 'kdrama_cleaned.csv' 파일이 성공적으로 저장되었습니다!")
        st.dataframe(df_cleaned.head(), use_container_width=True)