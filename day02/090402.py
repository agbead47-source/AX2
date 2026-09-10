
# 설문조사 앱
# 전송버튼, 체크박스, 라디오단추, 셀렉트박스, 멀티셀렉트박스, 슬라이더, 텍스트입력
# 위젯


import streamlit as st

st.title("📑미니 선호도 조사")
st.caption("위젯을 조작하면 화면 아래 '실시간 응답 요약'이 바로 바뀝니다.")

st.markdown("---")

# 1) 텍스트 입력 위젯 : key 를 지정해서 다른 위젯과 이름이 겹치지 않게 한다.
name = st.text_input("1) 이름을 입력하세요.", value="홍길동", key="widget_name")

# 2) 슬라이드 위젯 : 최소/ 최대/ 기본값 지정해 숫자로 선택하게 한다.
age = st.slider("2) 나이를 선택하세요" , min_value=10, max_value=80, value=25, key="widget_age")

# 3) 라디어 버튼 : 여러 선택지 중에서 하나만 고를 때 사용한다.
job = st.radio(
    " 3) 직군을 선택하세요",
    options=["학생","직장인","취준생","기타"],
    key="widget_job",
    # index=3 기타가 기본값일때
)

# 4) 셀레트 박스 (드롭다운) : 라디오와 비슷하지만 목록이 길때 공간을 절약할 수 있다.
country = st.selectbox(
    "4) 가장 관심있는 무역 상대국은 ?",
    options = ["미국", "중국", "일본", "베트남", "독일"],
    key="widget_country",
)

# 5) 멀티 셀렉트 박스 : 여러개를 동시에 선택할 수 있다.
interests = st.multiselect(
    "5) 관심 있는 데이터분야를 모두 고르세요.",
    options=["무역통계", "환율", "주가", "날씨", "인구통계"],
    key="widget_interests",
    default=["무역통계"]
)

# 6) 체크박스 : 참/ 거짓 값 하나를 받을 때
agree = st.checkbox("6) 강의 내용에 만족하시나요? ", key="widget_agree")

# 7) 슬라이더 만족 점수 1 ~ 5
score = st.slider("7) 이 강의 만족도 점수 (1~5점)" , min_value=1, max_value=5, value=5, key="widget_score")

# 8) 텍스트 영역: 여러줄의 입력 필요할 때 자유의견 입력
feedback = st.text_area("8) 자유롭게 의견을 남겨주세요.", key="widget_feedback")


# 9) 버튼 : 클릭 여부 (true/false)를 반환한다. 클릭했을때만 아래코드가 실행된다.
submitted = st.button("☑️제출하기", key="widget_submit_btn")

st.markdown("---")
st.subheader("📊실시간 응답 요약")



# 위젯 값들을 버튼을 누루지 않아도 조작하는 즉시 바로 갱신된다.

if submitted:
    st.write(f"- 이름: **{name}** / 나이 : **{age}**") 
    st.write(f"- 직군: **{job}** / 관심 국가 : **{country}**") 
    st.write(f"- 관심 분야 : **{ ','.join(interests) if interests else '선택없음' }**")
    st.write(f"- 강의 만족도 : **{ '만족' if agree else '미체크' }** / 만족도 점수: **{score}점**")
    st.write(f"- 자유의견 : **{ feedback if feedback else '작성안함' }**")

else:
    st.write('위 항목을 입력한 뒤 제출하기 버튼을 눌러주세요.')



