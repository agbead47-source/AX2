"""
타이타닉 데이터셋 기초 탐색
pandas head/tail/shape/info/columns 를 사용해서 데이터셋의 기본 정보를
화면에 순서대로 보여주는 streamlit 앱이다
실행방법 streamlit run 090701.py
"""

import io
import pandas as pd
import streamlit as st

# info_df = pd.DataFrame({
#     "타입" : df.dtypes,
#     "결측치 아닌 개수" : df.notna().sum(),
#     "결측치 개수" : df.isna().sum(),
# })
# st.dataframe(info_df, use_container_width=True)

# titanic.csv 가져오기
CSV_PATH="Titanic.csv"

# st.file_uploader로 파일을 직접 올릴 수 있다. 아무것도 올리지 않으면
# 아래의 기존 로직대로 같은 폴더 타이타닉 파일을 그대로 찾아서 읽는다
upload_file = st.file_uploader("Titanic.csv 파일을 직접 업로드 할 수 있습니다(선택사항)", type="csv")


st.title("🛳️타이타닉 데이터셋 기초 탐색")
st.caption("pandas의 head/tail/shape/info/columns로 데이터셋 기본 정보를 확인합니다.")

# 데이터프레임 변수 초기화
df = None

if upload_file is not None :
    df = pd.read_csv(upload_file)
else :
    try :
        # ❗수정됨: upload_file(None)이 아닌 CSV_PATH("Titanic.csv")를 읽도록 변경하여 에러 방지
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError :
        # 파일이 없을 때 보기 싫은 빨간 에러 창 대신 안내 메시지만 출력
        st.error("❌타이타닉 파일을 찾을 수가 없습니다.❌")
        st.info("같은 경로에 파일을 업로드 하거나 csv 파일을 폴더에 추가해 주세요.")

if df is not None : 
    st.subheader("1) head(): 데이터의 앞부분 5개 행 미리보기")
    st.dataframe(df.head(), use_container_width=True) # 기본행 5개

    st.subheader("2) tail(): 데이터의 뒷부분 5개 행 미리보기")
    st.dataframe(df.tail(), use_container_width=True) # 기본행 5개

    st.subheader("3) shape(): 행개수, 열개수")
    col1, col2 = st.columns(2)
    with col1 :
        st.metric("행 개수", f"{df.shape[0]}개")
    with col2 :
        st.metric("열 개수", f"{df.shape[1]}개")

    st.subheader("4) columns: 전체 열(컬럼) 이름 목록")
    # st.write(df.columns)
    st.write(list(df.columns))

    st.subheader("5) info() : 각 열의 자료형과 결측치(NaN) 여부 요약")
    # df.info 는 값을 리턴하지 않고 화면에 직접 출력만 해준 함수라서
    # io.StringIO() 라는 "메모리 위에 가짜 파일"에 결과를 받아낸 뒤 그 내용을 text로 보여준다.

    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

    st.success("기초 정보 확인이 끝났습니다. 다음 예제에서 전처리 필터링을 할게요. ")