import os
import requests
import feedparser
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드 (.env 파일에서 API 키 가져오기)
load_dotenv()  
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# 페이지 설정 (넓은 화면 적용)
st.set_page_config(page_title="환율 계산기", page_icon="💖", layout="wide")

# ==========================================
# 🎨 전체 화면 핑크 테마 & 굵은 글꼴 CSS 주입
# ==========================================
st.markdown("""
<style>
    /* 구글 웹 폰트 가져오기 (주아체, 고운돋움체) */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');

    /* 💡 전체 기본 글꼴 설정 (고운돋움 - 굵고 선명하게!) */
    html, body, [class*="st-"], p, span, div {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important; /* 글씨를 아주 굵게 */
        color: #5C3A41 !important; /* 또렷한 진한 브라운/핑크빛 */
    }

    /* 💡 제목류(h1, h2, h3) 글꼴 설정 (주아체 - 더 선명하고 둥글게) */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Jua', sans-serif !important;
        font-weight: 800 !important; /* 제목은 더더욱 굵게! */
    }
    
    /* 사이드바 글자 크기 살짝 키우기 */
    [data-testid="stSidebar"] * {
        font-size: 16px; 
    }

    /* 메인 화면 배경색 (연한 핑크) */
    .stApp {
        background-color: #FFF0F5;
    }
    
    /* 사이드바 배경색 (딸기우유 핑크) */
    [data-testid="stSidebar"] {
        background-color: #FFE4E1;
    }
    
    /* 상단 헤더 투명화 처리 */
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* 버튼 스타일 커스텀 (핑크 젤리 느낌 + 굵은 글씨) */
    div.stButton > button:first-child {
        background-color: #FFB6C1;
        color: #FFFFFF !important;
        font-family: 'Jua', sans-serif !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        border-radius: 20px;
        border: none;
        box-shadow: 0 4px 6px rgba(255, 105, 180, 0.3);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #FF69B4;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(255, 105, 180, 0.4);
        color: #FFF !important;
    }
</style>
""", unsafe_allow_html=True)

if not EXCHANGE_API_KEY:
    st.error("앗! 💦 환율 API 키가 설정되지 않았어요. .env 파일에 EXCHANGE_API_KEY를 추가해 주세요 🥺")
    st.stop()

# ==========================================
# 🔄 API 데이터 가져오기 (캐싱 적용)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_exchange_rates(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했어요 😭: {e}")
    return None

data = fetch_exchange_rates(EXCHANGE_API_KEY)

if data:
    rates = data.get("conversion_rates", {})
    krw_rate = rates.get("KRW", 1.0)
    
    # ==========================================
    # 🎀 1. 사이드바: 우리나라(KRW) 기준 비교 환율
    # ==========================================
    st.sidebar.markdown("<h2 style='color: #FF1493;'>🌍 주요 통화 환율 💖</h2>", unsafe_allow_html=True)
    st.sidebar.caption("우리나라 원화(KRW) 기준 실시간 환율이에요 ✨")
    st.sidebar.divider()
    
    usd_to_krw = krw_rate
    eur_to_krw = krw_rate / rates.get('EUR', 1)
    jpy_to_krw = (krw_rate / rates.get('JPY', 1)) * 100
    gbp_to_krw = krw_rate / rates.get('GBP', 1)
    cny_to_krw = krw_rate / rates.get('CNY', 1)
    
    st.sidebar.metric("🇺🇸 미국 (1 USD)", f"₩ {usd_to_krw:,.2f}")
    st.sidebar.metric("🇪🇺 유럽 (1 EUR)", f"₩ {eur_to_krw:,.2f}")
    st.sidebar.metric("🇯🇵 일본 (100 JPY)", f"₩ {jpy_to_krw:,.2f}")
    st.sidebar.metric("🇬🇧 영국 (1 GBP)", f"₩ {gbp_to_krw:,.2f}")
    st.sidebar.metric("🇨🇳 중국 (1 CNY)", f"₩ {cny_to_krw:,.2f}")
    
    st.sidebar.divider()
    st.sidebar.caption(f"📅 업데이트: {data.get('time_last_update_utc', '')[:16]} ⏰")

    # ==========================================
    # 💱 2. 메인 화면: 레이아웃 분할
    # ==========================================
    st.markdown("<h1 style='text-align: center; color: #FF1493; text-shadow: 2px 2px 4px #FFC0CB;'>💖환율 대시보드 💖</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FF69B4; font-size: 20px; font-weight: bold;'>실시간 맞춤 환율 계산과 최신 환율 변동 뉴스를 한눈에 확인하세요 🌸</p>", unsafe_allow_html=True)
    st.divider()
    
    left_col, right_col = st.columns([1.5, 1], gap="large")
    
    # ------------------------------------------
    # 🌷 좌측 영역: 환율 계산기
    # ------------------------------------------
    with left_col:
        st.markdown("<h3 style='color: #DB7093;'>🧚‍♀️ 나만의 맞춤 환율 계산기</h3>", unsafe_allow_html=True)
        
        all_currencies = list(rates.keys())
        favorite_currencies = ["USD", "KRW", "EUR", "JPY", "GBP", "CNY", "AUD", "CAD"]
        display_currencies = favorite_currencies + [c for c in all_currencies if c not in favorite_currencies]
        
        calc_col1, calc_col2 = st.columns(2)
        with calc_col1:
            from_currency = st.selectbox("👛 환전할 통화 (From)", display_currencies, index=0)
            amount = st.number_input("💸 변환할 금액을 입력하세요", min_value=0.0, value=1.0, step=1.0)
            
        with calc_col2:
            to_currency = st.selectbox("🛍️ 목표 통화 (To)", display_currencies, index=1)
            
        st.write("") 
        
        if st.button("💕 환율 계산하기 💕", use_container_width=True):
            if amount <= 0:
                st.warning("앗! 0보다 큰 금액을 입력해 주세요 🥺")
            else:
                rate_from = rates.get(from_currency)
                rate_to = rates.get(to_currency)
                conversion_result = (amount / rate_from) * rate_to
                unit_rate = rate_to / rate_from
                
                # 결과창
                st.markdown(f"""
                <div style="background-color: #FFFFFF; padding: 25px; border-radius: 20px; text-align: center; border: 3px dashed #FF69B4; box-shadow: 0 4px 10px rgba(255,105,180,0.2); margin-top: 15px;">
                    <h2 style="color: #FF1493; margin: 0; font-size: 36px; font-weight: 800; font-family: 'Jua', sans-serif;">
                        {amount:,.2f} {from_currency} <br><br>💘<br><br> <span style="color: #D11566;">{conversion_result:,.2f} {to_currency}</span>
                    </h2>
                    <hr style="margin: 20px 0; border: 0; border-top: 2px dotted #FFB6C1;">
                    <p style="color: #DB7093; font-size: 18px; margin: 0; font-weight: bold;">
                        ✨ 적용 환율: 1 {from_currency} = {unit_rate:,.4f} {to_currency} ✨
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # 📰 우측 영역: 대한민국 환율 관련 최신 기사
    # ------------------------------------------
    with right_col:
        st.markdown("<h3 style='color: #DB7093;'>🗞️ 실시간 국내 환율 뉴스</h3>", unsafe_allow_html=True)
        st.caption("구글 뉴스 기준 실시간 '환율' 관련 주요 기사예요 💌")
        
        kr_rss_url = "https://news.google.com/rss/search?q=환율&hl=ko&gl=KR&ceid=KR:ko"
        
        with st.spinner('최신 경제 뉴스를 예쁘게 포장해서 가져오는 중... 🎁'):
            kr_feed = feedparser.parse(kr_rss_url)
            
            if kr_feed.entries:
                for entry in kr_feed.entries[:6]:
                    st.markdown(f"**🎀 [{entry.title}]({entry.link})**")
                    published_date = entry.get('published', '발행일 정보 없음')
                    st.caption(f"🕒 {published_date}")
                    st.write("") 
            else:
                st.info("현재 환율 관련 뉴스를 불러올 수 없어요 힝 😢")

else:
    st.error("네트워크 오류 또는 API 이슈로 환율 정보를 가져오지 못했어요 😭")