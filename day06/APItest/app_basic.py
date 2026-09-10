# 날씨 API 실습
# OpenWeatherMap 현재 날씨 API로 특정 도시의 날씨를 가져와 출력한다
# 사전준비 OpenWeatherMap 회원가입하고 API 키 발급
# pip install requests python-dotenv
# .env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은 API 키 
# .env.example OPENWEATHER_API_KEY=your_key
# .env.example 받아서 .env로 이름바꾸고 자기 API를 채운다.
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드 (.env 파일에서 API 키 가져오기)
load_dotenv()  
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY") # 👈 새로 추가하신 환율 API 키

# 페이지 설정
st.set_page_config(page_title="글로벌 비즈니스 대시보드", page_icon="🌐", layout="centered")

st.title("🌐 글로벌 비즈니스 대시보드")
st.markdown("전 세계 날씨와 실시간 환율을 한눈에 확인해 보세요!")
st.divider()

# ==========================================
# 🌤️ 1. 실시간 날씨 정보 섹션
# ==========================================
st.header("🌤️ 실시간 날씨")

city = st.text_input("🔍 날씨를 알고 싶은 도시 이름을 영어로 입력하세요", value="Seoul")

if st.button("날씨 확인하기", use_container_width=True):
    if not WEATHER_API_KEY:
        st.error("앗! 날씨 API 키가 설정되지 않았습니다. .env 파일을 다시 확인해주세요.")
    elif not city:
        st.warning("도시 이름을 입력해주세요!")
    else:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
        
        with st.spinner('날씨 데이터를 불러오는 중입니다...'):
            try:
                weather_res = requests.get(weather_url)
                weather_data = weather_res.json()
                
                if weather_res.status_code == 200:
                    weather_desc = weather_data['weather'][0]['description']
                    icon = weather_data['weather'][0]['icon']
                    temp = weather_data['main']['temp']
                    feels_like = weather_data['main']['feels_like']
                    humidity = weather_data['main']['humidity']
                    wind_speed = weather_data['wind']['speed']
                    country = weather_data['sys']['country']
                    
                    st.subheader(f"📍 {city.capitalize()}, {country}의 현재 날씨")
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=100)
                    with col2:
                        st.markdown(f"### **{weather_desc}**")
                        st.markdown(f"**현재 기온:** {temp}℃")
                    
                    col3, col4, col5 = st.columns(3)
                    col3.metric("🌡️ 체감 온도", f"{feels_like}℃")
                    col4.metric("💧 습도", f"{humidity}%")
                    col5.metric("🌬️ 풍속", f"{wind_speed} m/s")
                    
                elif weather_data.get("cod") == "404":
                    st.error(f"'{city}' 도시를 찾을 수 없습니다. 영문 스펠링이 정확한지 확인해 주세요.")
                else:
                    st.error(f"날씨 오류가 발생했습니다: {weather_data.get('message')}")
                    
            except requests.exceptions.RequestException:
                st.error("날씨 데이터를 가져오는 중 문제가 발생했습니다.")

st.divider()

# ==========================================
# 💱 2. 실시간 환율 정보 섹션
# ==========================================
st.header("💱 실시간 환율 (1 USD 기준)")

if not EXCHANGE_API_KEY:
    st.error("환율 API 키가 설정되지 않았습니다. .env 파일에 EXCHANGE_API_KEY를 추가해 주세요.")
else:
    # ExchangeRate-API 호출 URL (기준 통화: USD)
    exchange_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"

    try:
        ex_res = requests.get(exchange_url)
        if ex_res.status_code == 200:
            ex_data = ex_res.json()
            
            # 최종 업데이트 시간 및 환율 데이터 추출
            last_update = ex_data.get('time_last_update_utc', '최신')
            rates = ex_data.get('conversion_rates', {})
            
            st.caption(f"📅 데이터 최종 업데이트: {last_update[:16]}")
            
            # 4개의 컬럼을 만들어 환율 정보를 깔끔하게 배치합니다.
            ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)
            
            ex_col1.metric("🇰🇷 원화 (KRW)", f"₩ {rates.get('KRW', 0):,.2f}")
            ex_col2.metric("🇪🇺 유로 (EUR)", f"€ {rates.get('EUR', 0):,.2f}")
            ex_col3.metric("🇯🇵 엔화 (JPY)", f"¥ {rates.get('JPY', 0):,.2f}")
            ex_col4.metric("🇬🇧 파운드 (GBP)", f"£ {rates.get('GBP', 0):,.2f}")
            
        else:
            st.error("환율 데이터를 불러오는 데 실패했습니다. API 키가 유효한지 확인해 주세요.")
    except requests.exceptions.RequestException:
        st.error("환율 API 요청 중 문제가 발생했습니다.")

import feedparser
import streamlit as st

# (기존 날씨, 환율 코드 아래에 추가)
st.divider()

# ==========================================
# 📰 3. 실시간 글로벌 경제 뉴스 (BBC Business)
# ==========================================
st.header("📰 실시간 글로벌 경제 뉴스")
st.caption("💡 데이터 제공: BBC News Business (API 키 불필요)")

# BBC 경제면 RSS URL
rss_url = "http://feeds.bbci.co.uk/news/business/rss.xml"

with st.spinner('최신 경제 뉴스를 불러오는 중입니다...'):
    # feedparser로 URL 데이터 읽어오기
    feed = feedparser.parse(rss_url)
    
    # 데이터가 정상적으로 불러와졌는지 확인
    if feed.entries:
        # 최신 기사 5개만 추출해서 보여주기
        for entry in feed.entries[:5]:
            # 기사 제목 (클릭 시 원문 링크 이동)
            st.markdown(f"#### 🔗 [{entry.title}]({entry.link})")
            
            # 발행 날짜
            st.caption(f"🕒 발행일: {entry.published}")
            
            # 기사 요약 내용
            st.write(entry.summary)
            
            st.write("") # 간격 띄우기
    else:
        st.error("뉴스를 불러오는 데 실패했습니다.")