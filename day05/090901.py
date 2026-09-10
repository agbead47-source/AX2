import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

# --------------------------------------------------
# 📁 0. 자동 경로 설정 (클라우드 & 로컬 모두 호환!)
# --------------------------------------------------
# 현재 실행 중인 파일(090901.py)을 기준으로 상위 폴더(AX2)를 찾습니다.
BASE_DIR = Path(__file__).resolve().parents[1]

# --------------------------------------------------
# 🌸 1. 귀여운 핑크색 테마 설정 (CSS)
# --------------------------------------------------
st.set_page_config(page_title="무역 분석 대시보드", page_icon="🎀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    [data-testid="stSidebar"] { background-color: #FFE4E1; }
    h1, h2, h3 { color: #FF69B4 !important; font-weight: bold; }
    hr { border-top: 2px dashed #FFB6C1; }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 🎨 2. 한글 폰트 설정 (차트 폰트 강제 등록)
# --------------------------------------------------
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from pathlib import Path

# 현재 파일이 있는 경로에서 malgun.ttf 파일을 찾습니다.
CURRENT_DIR = Path(__file__).resolve().parent
font_path = CURRENT_DIR / "malgun.ttf"

plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

if font_path.exists():
    # 🌟 핵심: Matplotlib 폰트 매니저에 강제로 폰트 파일을 등록합니다.
    fm.fontManager.addfont(str(font_path))
    
    # 등록한 폰트의 실제 이름을 가져와서 기본 폰트로 설정합니다.
    font_name = fm.FontProperties(fname=str(font_path)).get_name()
    plt.rc('font', family=font_name)
else:
    # 폰트 파일이 없을 경우의 예외 처리
    try:
        plt.rc('font', family='Malgun Gothic')
    except:
        pass

# --------------------------------------------------
# 📂 3. 데이터 불러오기 및 전처리
# --------------------------------------------------
@st.cache_data
def load_data():
    try:
        # common 폴더 안의 데이터를 자동으로 찾아갑니다.
        baci_file = BASE_DIR / "common" / "baci_85_sample.csv"
        country_file = BASE_DIR / "common" / "country_codes_sample.csv"
        
        df_baci = pd.read_csv(baci_file)
        df_code = pd.read_csv(country_file)
        
        # 'j' 컬럼을 기준으로 두 데이터 병합
        df = pd.merge(df_baci, df_code, on='j', how='left')
        
        # 영문 컬럼명을 한글로 변경
        df.rename(columns={
            't': '연도', 
            'v': '수출액', 
            'country_name': '국가명'
        }, inplace=True)
        
        # 무역액 등급 (대, 중, 소) 파생 변수 생성
        if '수출액' in df.columns:
            df['수출액'] = df['수출액'].fillna(0) 
            df['무역액 등급'] = pd.qcut(df['수출액'], q=3, labels=['소', '중', '대'], duplicates='drop')
            
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 에러 발생: {e}")
        return pd.DataFrame()

df_raw = load_data()

# --------------------------------------------------
# 🎀 4. 화면 레이아웃 (오른쪽 메인 화면)
# --------------------------------------------------
st.title("🎀 무역 분석 대시보드 🎀")
st.markdown("---")

if not df_raw.empty:
    st.subheader("🧹 1. 결측치 처리 현황")
    missing_before = df_raw.isnull().sum().sum()
    df_clean = df_raw.dropna()
    missing_after = df_clean.isnull().sum().sum()
    
    col_m1, col_m2 = st.columns(2)
    col_m1.info(f"원본 결측치 총 개수: **{missing_before}개**")
    col_m2.success(f"제거 후 결측치 총 개수: **{missing_after}개** 🧼")
    st.markdown("---")
    
    # --------------------------------------------------
    # 🎛️ 5. 사이드바 (Sidebar) 필터 설정
    # --------------------------------------------------
    st.sidebar.header("🔍 대시보드 필터")
    
    if '국가명' in df_clean.columns:
        country_list = df_clean['국가명'].unique().tolist()
    else:
        country_list = []
        
    selected_countries = st.sidebar.multiselect(
        "🌎 국가 선택", 
        options=country_list, 
        default=country_list[:5] if len(country_list) >= 5 else country_list
    )
    
    selected_grades = st.sidebar.multiselect(
        "📊 무역액 등급 선택", 
        options=['대', '중', '소'], 
        default=['대', '중', '소']
    )
    
    filtered_df = df_clean[
        (df_clean['국가명'].isin(selected_countries)) & 
        (df_clean['무역액 등급'].isin(selected_grades))
    ]

    # --------------------------------------------------
    # 💡 6. 분석 및 시각화
    # --------------------------------------------------
    st.subheader("💰 2. 요약 지표")
    if filtered_df.empty:
        st.warning("선택한 필터 조건에 맞는 데이터가 없습니다! 🥺")
    else:
        col1, col2 = st.columns(2)
        col1.metric("총 거래건수", f"{len(filtered_df):,} 건")
        col2.metric("총 수출액 (달러)", f"${filtered_df['수출액'].sum():,.2f}")
    st.markdown("---")
    
    st.subheader("🔥 3. 국가별 연도 수출액 히트맵 및 등급 분포")
    if not filtered_df.empty:
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**국가 x 연도별 수출액 히트맵 (상위 8개국)**")
            top8_countries = filtered_df.groupby('국가명')['수출액'].sum().nlargest(8).index
            df_top8 = filtered_df[filtered_df['국가명'].isin(top8_countries)]
            pivot_df = df_top8.pivot_table(index='국가명', columns='연도', values='수출액', aggfunc='sum')
            
            if not pivot_df.empty and not pivot_df.isnull().all().all():
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                sns.heatmap(pivot_df, cmap="RdPu", annot=False, fmt=".0f", linewidths=.5, ax=ax1)
                st.pyplot(fig1)
            else:
                st.info("히트맵 데이터가 부족합니다.")

        with col4:
            st.markdown("**무역액 등급 분포**")
            grade_counts = filtered_df['무역액 등급'].value_counts().reindex(['대', '중', '소'])
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.barplot(x=grade_counts.index, y=grade_counts.values, hue=grade_counts.index, palette="spring", legend=False, ax=ax2)
            ax2.set_ylabel("데이터 건수")
            st.pyplot(fig2)
    st.markdown("---")
    
    st.subheader("🏆 4. 상위 5개국 무역액 등급 교차표")
    if not filtered_df.empty:
        top5_countries = filtered_df.groupby('국가명')['수출액'].sum().nlargest(5).index
        df_top5 = filtered_df[filtered_df['국가명'].isin(top5_countries)]
        
        if not df_top5.empty:
            tab1, tab2 = st.tabs(["🔢 원본 건수", "📊 정규화 비율(%)"])
            with tab1:
                cross_raw = pd.crosstab(df_top5['국가명'], df_top5['무역액 전급'] if '무역액 전급' in df_top5 else df_top5['무역액 등급'])
                st.dataframe(cross_raw.style.background_gradient(cmap='RdPu'), use_container_width=True)
            with tab2:
                cross_norm = pd.crosstab(df_top5['국가명'], df_top5['무역액 등급'], normalize='index') * 100
                st.dataframe(cross_norm.round(1).style.background_gradient(cmap='RdPu'), use_container_width=True)
        else:
            st.info("상위 5개국 데이터가 없습니다.")
else:
    st.error("데이터를 로드하지 못했습니다. 파일 위치를 다시 확인해 주세요.")