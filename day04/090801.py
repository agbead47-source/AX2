# trade.csv 파일 활용 (AX2/common/trade.csv)
# HS코드가 
# 85로 시작하는 (반도체류)  + 국가명 미국 또는 베트남 + 수출금액 0보다 큰수(실제 수출실적이 있는) 행만
# 다중 조건 으로 필터링 한 뒤, 수출 금액 상위 10건을 화면에 보여주고 report.csvf로 저장
# streamlit 사용 streamlit run 090801.py

import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="반도체류 수출 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 반도체류 수출 데이터 분석")
st.write("HS코드 85로 시작하는 미국·베트남 수출 실적 분석")

# --------------------------------------------------
# 2. 파일 경로
# --------------------------------------------------

# 현재 파일 : AX2/day04/090801.py
# 데이터 파일 : AX2/common/trade.csv

BASE_DIR = Path(__file__).resolve().parents[1]

file_path = BASE_DIR / "common" / "trade.csv"
report_path = BASE_DIR / "common" / "report.csv"


# --------------------------------------------------
# 3. CSV 파일 불러오기
# --------------------------------------------------

try:
    df = pd.read_csv(file_path, encoding="utf-8-sig")

except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding="cp949")

except FileNotFoundError:
    st.error(f"파일을 찾을 수 없습니다: {file_path}")
    st.stop()


# --------------------------------------------------
# 4. 데이터 전처리
# --------------------------------------------------

# 컬럼명 공백 제거
df.columns = df.columns.str.strip()

# HS코드를 문자열로 변경
df["hs_code"] = df["hs_code"].astype(str)

# 수출금액을 숫자형으로 변경
df["수출금액"] = pd.to_numeric(
    df["수출금액"],
    errors="coerce"
)

# --------------------------------------------------
# 5. 다중 조건 필터링
# --------------------------------------------------

condition = (
    df["hs_code"].str.startswith("85")
    & df["국가명"].isin(["미국", "베트남"])
    & (df["수출금액"] > 0)
    & (df["수출입구분"] == "Export")
)

filtered_df = df[condition].copy()


# --------------------------------------------------
# 6. 수출금액 상위 10건
# --------------------------------------------------

top10 = (
    filtered_df
    .sort_values(
        by="수출금액",
        ascending=False
    )
    .head(10)
)


# --------------------------------------------------
# 7. 요약 정보
# --------------------------------------------------

st.divider()

st.subheader("📌 수출 데이터 요약")

total_count = len(filtered_df)

total_export = filtered_df["수출금액"].sum()

average_export = filtered_df["수출금액"].mean()

max_export = filtered_df["수출금액"].max()


# 4개의 칸으로 표시
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "수출 건수",
    f"{total_count:,}건"
)

col2.metric(
    "총 수출금액",
    f"{total_export:,.0f}"
)

col3.metric(
    "평균 수출금액",
    f"{average_export:,.0f}"
)

col4.metric(
    "최대 수출금액",
    f"{max_export:,.0f}"
)


# --------------------------------------------------
# 8. 국가별 요약
# --------------------------------------------------

st.divider()

st.subheader("🌏 국가별 수출 요약")

country_summary = (
    filtered_df
    .groupby("국가명")["수출금액"]
    .agg(["count", "sum", "mean"])
    .reset_index()
)

country_summary.columns = [
    "국가명",
    "수출건수",
    "총수출금액",
    "평균수출금액"
]

st.dataframe(
    country_summary,
    use_container_width=True
)


# --------------------------------------------------
# 9. 국가별 수출금액 그래프
# --------------------------------------------------

st.subheader("📊 국가별 총 수출금액")

country_chart = (
    filtered_df
    .groupby("국가명")["수출금액"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(country_chart)


# --------------------------------------------------
# 10. 수출금액 상위 10건
# --------------------------------------------------

st.divider()

st.subheader("🏆 수출금액 상위 10건")

st.dataframe(
    top10,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 11. 상위 10건 그래프
# --------------------------------------------------

st.subheader("📈 수출금액 TOP 10")

# 그래프에서 품목명과 국가를 같이 표시
chart_df = top10.copy()

chart_df["품목/국가"] = (
    chart_df["품목명"]
    + " / "
    + chart_df["국가명"]
)

chart_df = chart_df.set_index("품목/국가")

st.bar_chart(
    chart_df["수출금액"]
)


# --------------------------------------------------
# 12. 품목별 수출 요약
# --------------------------------------------------

st.divider()

st.subheader("📦 주요 품목별 수출금액")

item_summary = (
    filtered_df
    .groupby("품목명")["수출금액"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(item_summary)


# --------------------------------------------------
# 13. 간단한 분석 문장
# --------------------------------------------------

st.divider()

st.subheader("📝 분석 요약")

if not filtered_df.empty:

    top_country = (
        filtered_df
        .groupby("국가명")["수출금액"]
        .sum()
        .idxmax()
    )

    top_item = (
        filtered_df
        .groupby("품목명")["수출금액"]
        .sum()
        .idxmax()
    )

    st.write(
        f"""
        조건에 해당하는 수출 데이터는 총 **{total_count:,}건**입니다.

        총 수출금액은 **{total_export:,.0f}**이며,
        평균 수출금액은 **{average_export:,.0f}**입니다.

        미국과 베트남 중 총 수출금액이 가장 높은 국가는
        **{top_country}**입니다.

        수출금액 기준 가장 주요한 품목은
        **{top_item}**입니다.
        """
    )

else:
    st.warning("조건에 해당하는 데이터가 없습니다.")


# --------------------------------------------------
# 14. report.csv 저장
# --------------------------------------------------

top10.to_csv(
    report_path,
    index=False,
    encoding="utf-8-sig"
)

st.success(
    f"✅ 수출금액 상위 10건이 report.csv로 저장되었습니다.\n\n{report_path}"
)


# --------------------------------------------------
# 15. CSV 다운로드 버튼
# --------------------------------------------------

csv = top10.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 report.csv 다운로드",
    data=csv,
    file_name="report.csv",
    mime="text/csv"
)