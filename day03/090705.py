# streamlit run 090705.py

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager

st.title("📊 인코딩 자동감지 + 막대그래프 (🛳️Titanic 연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실등급별 생존율을 그래프로 그립니다.")

# 파일 경로 설정
CSV_PATH = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
FONT_PATH = os.path.join(os.path.dirname(__file__), "Amsterdam.ttf")

# 1) 다중 인코딩 시도 함수
def read_csv_with_auto_encoding(file_path):
    encodings = ["utf-8-sig", "cp949", "euc-kr"] 
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df, encoding
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            st.error(f"'{file_path}' 파일을 찾을 수 없습니다.")
            return None, None
            
    st.error("지원하는 인코딩 형식으로 파일을 읽을 수 없습니다.")
    return None, None

# 인코딩 자동 감지로 CSV 읽기
st.subheader("1) 인코딩 자동 감지")

# 수정 1: 반환값이 2개(df, encoding)이므로 두 변수로 받아야 합니다.
df, encoding = read_csv_with_auto_encoding(CSV_PATH)

# 파일이 정상적으로 읽혔을 때만 아래 코드를 실행하도록 방어 코드 추가
if df is not None:
    st.success(f"'{encoding}' 인코딩으로 파일을 성공적으로 읽었습니다.")
    
    st.markdown("---")
    st.subheader("2) 객실등급별 생존율")
    
    # 수정 2: 'survied' 오타 수정, sort() 대신 sort_index() 사용
    # 타이타닉 데이터의 컬럼명 대소문자에 유의하세요. (일반적으로 Pclass, Survived 입니다)
    try:
        pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()
    except KeyError:
        # 혹시 컬럼명이 소문자인 경우를 위한 대비
        pclass_survival_rate = df.groupby("pclass")["survived"].mean().sort_index()
    
    # 수정 3: pclass_survivaㅣ_ rate -> pclass_survival_rate (한글 'ㅣ' 오타 수정)
    st.dataframe((pclass_survival_rate * 100).round(1).rename("생존율(%)"))

    st.markdown("---")
    st.subheader("3) 객실등급별 생존율 막대그래프")
    
    try: 
        # 폰트파일이 없으면 FileNotFoundError
        font_prop = font_manager.FontProperties(fname=FONT_PATH)
        font_manager.fontManager.addfont(FONT_PATH)
        plt.rcParams['font.family'] = font_prop.get_name()
        st.write("Amsterdam 폰트를 적용했습니다.")
    except FileNotFoundError:
        st.warning("Amsterdam 폰트파일을 찾을 수가 없습니다.")

    fig, ax = plt.subplots(figsize=(8,5))
    
    (pclass_survival_rate * 100).plot(kind="bar", color="blue", ax=ax)
    
    ax.tick_params(axis='x', labelrotation=0)
    
    ax.set_title("객실 등급별 생존율")
    ax.set_xlabel("객실등급(Pclass)")
    ax.set_ylabel("생존율(%)")

    st.pyplot(fig)

    output_png = output_path = os.path.join(os.path.dirname(__file__))
    fig.savefig("chart.png")
    st.success("그래프가 'chart.png'로 저장되었습니다.")

    #hi