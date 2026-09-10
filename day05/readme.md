무역 분석 대시보드
사이드바에 국가 선택, 무역액 등급 선택(대, 중, 소) 필터
baci_85_sample.csv (C:\Users\user\AX2\common)
country_codes_sample.csv (C:\Users\user\AX2\common)사용
streamlit 사용
한글지원 Amsterdam.ttff 사용 (경로:C:\Users\user\AX2\day03\Amsterdam.ttf)
핑크색으로 귀엽게 만들어줘



오른쪽 화면에

1. 타이틀 : 무역 분석 대시보드
st.markdown("---")
2. baci_85_sample.csv 파일의 결측치 처리
st.markdown("---")
3. 총 거래건수    총 수출액(달러)

st.markdown("---")
4. 국가*연도 수출액 히트맵(상위 8개국) 무역액 등급분포

st.markdown("---")
5. 상위 5개국 * 무역액 등급 교차표
    원본건수      정규화비율