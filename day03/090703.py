"""
타이타닉 데이터 필터링, 결측치 정리
age(나이)가 35 이상인 승객 필터링
성별별로 필터링
titanic_cleaned.csv 로 저장
실행방법 : streamlit run 090703.py
"""

import pandas as pd
import streamlit as st

st.title("🛳️타이타닉 데이터 필터링 & 결측치 정리")
st.caption("나이＊성별 조건으로 필터링해보고, 결측치를 제거해서 새 csv로 저장합니다.")

CSV_PATH = "Titanic.csv"

try: 
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    st.error("Titanic.csv 파일을 찾을 수 없습니다.")
else: 
    st.metric("원본 데이터 행 개수", f"{len(df)}행")

    st.markdown("---")
    
    # 0) 결측치 정리 (Age 컬럼 기준)
    st.subheader("0) 결측치 정리")
    df_cleaned = df.dropna(subset=['Age'])
    st.write(f"나이 결측치 제거 후 데이터 : **{len(df_cleaned)}행**")
    
    st.markdown("---")

    # 1) Age 35세 이상 필터링
    st.subheader("1) 나이 35세 이상 승객")
    over_35 = df_cleaned[df_cleaned["Age"] >= 35]
    
    st.write(f"나이 35세 이상 승객수 : **{len(over_35)}명**")
    st.dataframe(over_35[["Name", "Sex", "Age"]].head(), use_container_width=False)
    
    st.markdown("---")
    
    # 2) 성별 여자 남자 필터링 2컬럼 사용
    st.subheader("2) 성별 필터링 결과")
    female_df = df_cleaned[df_cleaned["Sex"] == "female"]
    male_df = df_cleaned[df_cleaned["Sex"] == "male"] 

    col1, col2 = st.columns(2)
    with col1 :
        st.metric("여성 승객수", f"{len(female_df)}명")
    with col2 :
        st.metric("남성 승객수", f"{len(male_df)}명")

    st.markdown("---")

    # 3) 두 조건을 동시에 만족하는 행(35세 이상 여성)
    st.subheader("3) 35세 이상 & 여성 승객")
    
    # 다중 조건은 & 기호를 사용하고, 각 조건을 괄호()로 묶어줍니다.
    over_35_female = df_cleaned[(df_cleaned["Age"] >= 35) & (df_cleaned["Sex"] == "female")]
    
    st.write(f"35세 이상 여성 승객수 : **{len(over_35_female)}명**")
    st.dataframe(over_35_female[["Name", "Sex", "Age"]].head(), use_container_width=False)

    st.markdown("---")

    # 나이의 결측치(NaN) 확인 및 dropna 처리
    st.subheader("4) Age 결측치 처리")
    missing_age_count = df["Age"].isna().sum() #isna()는 결측치면 True 반환
    st.write(f"AGE 열의 결측치 개수: **{missing_age_count}개**")

    # subset = ["Age"]: AGE 열이 결측치인 행만 골라서 제거한다.
    df_clean = df.dropna(subset = ["Age"])
    col1, col2 = st.columns(2)
    with col1:
        st.metric("제거 전", f"{len(df)}행")
    with col1:
            st.metric("제거 후", f"{len(df_clean)}행")

    # 정리된 데이터를 csv 파일로 저장
    output_path = "titanic_cleaned.csv"
    df_clean.to_csv(output_path, index = False)
    st.success("파일을 저장했습니다")
    st.dataframe(df_clean.head(), use_container_width=True)

