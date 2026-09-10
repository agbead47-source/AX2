
# random 모듈을 이용해서 1~45 중 중복 없는 번호 6개를 뽑고
# 자료 구조 set , 버튼을 누르면 5세트를 한번에 생성
# datetime으로 생성 시간도 함께 보여준다,
# lotto V2.0



import streamlit as st
import random
from datetime import datetime

# 번호에 맞는 색깔 이모지를 붙여주는 함수
def get_emoji_number(number):
    if number <= 10:
        return f"🟡 {number}"   # 1~10: 노랑
    elif number <= 20:
        return f"🔵 {number}"   # 11~20: 파랑
    elif number <= 30:
        return f"🔴 {number}"   # 21~30: 빨강
    elif number <= 40:
        return f"⚫ {number}"   # 31~40: 검정
    else:
        return f"🟢 {number}"   # 41~45: 초록

# 화면 구성
st.title("❤️로또 번호 자동 생성기❤️")
st.caption("🍀버튼을 누르면 1~45의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다.🍀")

st.markdown("---")

# 버튼 클릭 시 동작
if st.button("🤞5세트 번호 생성하기🤞"):
    
    # 시간 출력
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"⏱️ **생성 시각:** {now_str}")
    st.write("") # 한 줄 띄우기
    
    # 5세트 생성 및 출력
    for i in range(1, 6):
        # 1. 번호 6개 뽑기
        numbers = set()
        while len(numbers) < 6:
            numbers.add(random.randint(1, 45))
        
        # 2. 오름차순 정렬
        sorted_nums = sorted(numbers)
        
        # 3. 각 번호에 이모지 붙이기
        emoji_nums = [get_emoji_number(num) for num in sorted_nums]
        
        # 4. 보기 좋게 띄어쓰기로 연결해서 출력하기
        result_text = " ㅤ ".join(emoji_nums)  # 번호 사이 간격
        st.subheader(f"{i}세트 : {result_text}")

st.markdown("---")