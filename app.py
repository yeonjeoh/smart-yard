import streamlit as st
import pandas as pd

# ── 페이지 설정 ───────────────────────────────────────────
st.set_page_config(
    page_title="스마트 야드 MRO 통제 대시보드",
    page_icon="⚓",
    layout="wide"
)

# ── 데이터 불러오기 및 계산 함수 ─────────────────────────
@st.cache_data  # 같은 파일이면 다시 읽지 않고 캐시 사용 (속도 최적화)
def load_data():
    df_process = pd.read_csv("data/공정스케줄.csv")
    df_stock = pd.read_csv("data/자재재고.csv")

    # 날짜 변환
    date_cols = ["계획시작일", "계획종료일", "실제시작일", "실제종료일"]
    for col in date_cols:
        df_process[col] = pd.to_datetime(df_process[col])

    # EVM: SPI 계산
    df_process["SPI"] = df_process["실적공수"] / df_process["계획공수"]

    # ROP 계산
    df_stock["ROP계산값"] = (
        df_stock["일평균사용량"] * df_stock["조달기간(일)"] + df_stock["안전재고"]
    )
    df_stock["발주필요"] = df_stock["현재고"] < df_stock["ROP계산값"]

    return df_process, df_stock

df_process, df_stock = load_data()

# ── 사이드바 ─────────────────────────────────────────────
with st.sidebar:
    st.title("⚓ 스마트 야드")
    st.markdown("---")
    selected_ship = st.selectbox(
        "함정 선택",
        ["PKG-719 천안함", "FFG-815 충남함", "SS-083 나대용함"]
    )
    selected_period = st.selectbox(
        "정비 기간",
        ["2026년 1분기", "2026년 2분기", "2025년 4분기"]
    )
    st.markdown("---")
    st.caption("ver 0.2 | 스마트 야드 AX팀")

# ── 메인 타이틀 ───────────────────────────────────────────
st.title(f"⚓ {selected_ship} — MRO 통제 현황")
st.caption(f"정비 기간: {selected_period}")
st.markdown("---")

# ── KPI 카드: 실제 계산값 반영 ───────────────────────────
delayed = df_process[df_process["SPI"] < 1.0]
shortage = df_stock[df_stock["발주필요"] == True]
avg_spi = df_process["SPI"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📊 평균 공정 달성률 (SPI)",
        value=f"{avg_spi:.2f}",
        delta=f"지연 {len(delayed)}건"
    )
with col2:
    st.metric(
        label="⚠️ 지연 작업",
        value=f"{len(delayed)}건",
        delta=f"전체 {len(df_process)}건 중",
        delta_color="inverse"  # 숫자 클수록 빨간색
    )
with col3:
    st.metric(
        label="🚨 즉시 발주 필요",
        value=f"{len(shortage)}건",
        delta=f"전체 {len(df_stock)}품목 중",
        delta_color="inverse"
    )

st.markdown("---")

# ── 탭 3개 ───────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 공정 현황 (EVM)", "📦 재고 현황 (ROP)", "🤖 AI 브리핑"])

with tab1:
    st.subheader("공정 현황 — EVM 분석")

    # SPI 기준으로 색상 구분
    def highlight_spi(val):
        if val >= 1.0:
            return "background-color: #d4edda"  # 초록
        elif val >= 0.8:
            return "background-color: #fff3cd"  # 노랑
        else:
            return "background-color: #f8d7da"  # 빨강

    styled = df_process[["작업명", "담당부서", "계획공수", "실적공수", "SPI"]].style.map(
        highlight_spi, subset=["SPI"]
    )
    st.dataframe(styled, use_container_width=True)

    st.markdown("#### ⚠️ 지연 작업 목록")
    st.dataframe(delayed[["작업명", "담당부서", "SPI"]], use_container_width=True)

with tab2:
    st.subheader("재고 현황 — ROP 분석")
    st.dataframe(
        df_stock[["품목명", "현재고", "ROP계산값", "발주필요"]],
        use_container_width=True
    )

    st.markdown("#### 🚨 즉시 발주 필요 품목")
    st.dataframe(shortage[["품목명", "현재고", "ROP계산값"]], use_container_width=True)

with tab3:
    st.subheader("🤖 AI 브리핑 — Claude Sonnet")

    # ── 브리핑 버튼 ───────────────────────────────────────
    if st.button("🚀 AI 브리핑 생성", type="primary"):

        # 실제 DataFrame에서 뽑은 데이터를 프롬프트에 삽입
        briefing_data = f"""
[공정 지연 현황] (SPI < 1.0 인 작업)
{delayed[["작업명", "담당부서", "SPI"]].to_string(index=False)}

[재고 부족 현황] (현재고 < ROP 인 품목)
{shortage[["품목명", "현재고", "ROP계산값"]].to_string(index=False)}
"""

        with st.spinner("Claude가 분석 중입니다..."):
            import os
            from dotenv import load_dotenv
            import anthropic

            api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""당신은 함정 수리창의 MRO 관제 AI입니다.
아래 데이터를 분석하여 수리창 담당자에게 브리핑하세요.
우선순위가 높은 순서로 3가지 조치사항을 간결하게 제시하세요.

{briefing_data}"""
                    }
                ]
            )

        st.markdown(message.content[0].text)