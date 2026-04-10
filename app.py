import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['font.family'] = 'Malgun Gothic'

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

# ── 탭 8개 ───────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 공정 현황 (EVM)",
    "📦 재고 현황 (ROP)",
    "🤖 AI 브리핑",
    "⚙️ RAM 분석",
    "🎲 Monte Carlo",
    "📉 와이블 분석",
    "👥 인력 최적화",
    "🔮 예측 정비"
])
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
with tab4:
    st.subheader("⚙️ RAM 분석 — 장비 가용도 계산")

    st.markdown("#### 장비 정보 입력")

    col1, col2 = st.columns(2)

    with col1:
        # 사용자가 직접 MTBF 입력
        mtbf_input = st.number_input(
            "MTBF (평균 고장 간격, 시간)",
            min_value=100,
            max_value=50000,
            value=4380,
            step=100,
            help="과거 데이터 기반 평균 고장 간격을 입력하세요"
        )
        st.caption(f"= 약 {mtbf_input/24:.0f}일 = 약 {mtbf_input/24/30:.1f}개월")

    with col2:
        # 사용자가 직접 MTTR 입력
        mttr_input = st.number_input(
            "MTTR (평균 수리 시간, 시간)",
            min_value=1,
            max_value=1000,
            value=44,
            step=1,
            help="과거 데이터 기반 평균 수리 시간을 입력하세요"
        )
        st.caption(f"= 약 {mttr_input/24:.1f}일")

    # 가용도 계산
    availability = mtbf_input / (mtbf_input + mttr_input)

    st.markdown("---")
    st.markdown("#### 계산 결과")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="가용도 (A)",
            value=f"{availability*100:.2f}%",
            delta="목표 99% 대비 " + f"{(availability-0.99)*100:+.2f}%p"
        )
    with col2:
        st.metric(
            label="연간 가동 시간",
            value=f"{availability*8760:.0f}시간",
            delta=f"연간 {(1-availability)*8760:.0f}시간 정비"
        )
    with col3:
        # 가용도 목표 달성 여부
        if availability >= 0.99:
            st.success("✅ 목표 가용도 달성 (99% 이상)")
        elif availability >= 0.95:
            st.warning("⚠️ 주의 (95~99%)")
        else:
            st.error("🚨 위험 (95% 미만)")

    # RAM 개선 시나리오
    st.markdown("---")
    st.markdown("#### MTTR 단축 시나리오")
    st.caption("MTTR을 줄이면 가용도가 어떻게 개선되는지 확인합니다")

    import pandas as pd
    scenarios = []
    for mttr_scenario in [mttr_input, mttr_input*0.8, mttr_input*0.6, mttr_input*0.4]:
        a = mtbf_input / (mtbf_input + mttr_scenario)
        scenarios.append({
            "MTTR (시간)": f"{mttr_scenario:.0f}",
            "가용도": f"{a*100:.2f}%",
            "목표 달성": "✅" if a >= 0.99 else "❌"
        })

    st.dataframe(pd.DataFrame(scenarios), use_container_width=True)


with tab5:
    st.subheader("🎲 Monte Carlo 시뮬레이션 — 가용도 리스크 분석")

    st.markdown("#### 불확실성 범위 설정")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**MTBF 범위 (시간)**")
        mtbf_min = st.number_input("MTBF 최솟값", value=3000, step=100)
        mtbf_mode = st.number_input("MTBF 최빈값", value=4380, step=100)
        mtbf_max = st.number_input("MTBF 최댓값", value=6000, step=100)

    with col2:
        st.markdown("**MTTR 범위 (시간)**")
        mttr_min = st.number_input("MTTR 최솟값", value=30, step=1)
        mttr_mode = st.number_input("MTTR 최빈값", value=44, step=1)
        mttr_max = st.number_input("MTTR 최댓값", value=80, step=1)

    if st.button("🚀 시뮬레이션 실행", type="primary"):
        import numpy as np

        N = 10000
        np.random.seed(42)

        # 삼각분포로 MTBF/MTTR 생성
        MTBF_sim = np.random.triangular(mtbf_min, mtbf_mode, mtbf_max, N)
        MTTR_sim = np.random.triangular(mttr_min, mttr_mode, mttr_max, N)
        A_sim = MTBF_sim / (MTBF_sim + MTTR_sim)

        # 결과 지표
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("평균 가용도", f"{np.mean(A_sim)*100:.2f}%")
        with col2:
            st.metric("99% 달성 확률", f"{np.mean(A_sim >= 0.99)*100:.1f}%")
        with col3:
            st.metric("하위 5% 가용도", f"{np.percentile(A_sim, 5)*100:.2f}%")

        # 히스토그램
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(A_sim * 100, bins=50, color='mediumseagreen',
                edgecolor='white', alpha=0.8)
        ax.axvline(99, color='red', linestyle='--',
                   linewidth=2, label='목표 가용도 99%')
        ax.axvline(np.mean(A_sim) * 100, color='orange', linestyle='--',
                   linewidth=2, label=f'평균: {np.mean(A_sim)*100:.2f}%')
        ax.set_title('가용도(A) 분포 — Monte Carlo 시뮬레이션')
        ax.set_xlabel('가용도 (%)')
        ax.set_ylabel('빈도')
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)

        # 해석
        prob_99 = np.mean(A_sim >= 0.99) * 100
        if prob_99 >= 80:
            st.success(f"✅ 목표 가용도 99% 달성 확률 {prob_99:.1f}% — 안정적입니다.")
        elif prob_99 >= 50:
            st.warning(f"⚠️ 목표 가용도 99% 달성 확률 {prob_99:.1f}% — MTTR 단축이 필요합니다.")
        else:
            st.error(f"🚨 목표 가용도 99% 달성 확률 {prob_99:.1f}% — 즉각적인 개선이 필요합니다.")
with tab6:
    st.subheader("📉 와이블 분석 — 예방정비 최적 시점 계산")
    st.caption("장비 고장 이력 데이터를 입력하면 β/η를 추정하고 예방정비 시점을 자동 계산합니다.")

    st.markdown("#### 와이블 파라미터 직접 입력")
    st.caption("고장 데이터가 없는 경우 전문가 판단으로 직접 입력하세요.")

    col1, col2 = st.columns(2)
    with col1:
        beta_input = st.number_input(
            "β (형상 모수)",
            min_value=0.1, max_value=10.0, value=2.5, step=0.1,
            help="β<1: 초기불량기 / β=1: 안정기 / β>1: 마모기"
        )
        if beta_input < 1:
            st.warning("초기불량기 — 납품 초기 집중 모니터링 필요")
        elif beta_input == 1:
            st.info("안정기 — MTBF 기반 정기 예방정비 적용")
        else:
            st.error("마모기 — 예방정비 주기 단축 필요")

    with col2:
        eta_input = st.number_input(
            "η (특성 수명, 시간)",
            min_value=100, max_value=100000, value=5000, step=100,
            help="전체 장비의 63.2%가 고장나는 시점"
        )
        st.caption(f"= 약 {eta_input/24:.0f}일 = 약 {eta_input/24/30:.1f}개월")

    target_r = st.slider(
        "목표 신뢰도 (%)",
        min_value=80, max_value=99, value=90, step=1
    )

    # 예방정비 시점 계산
    import numpy as np
    t_pm = eta_input * (-np.log(target_r/100))**(1/beta_input)

    st.markdown("---")
    st.markdown("#### 계산 결과")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=f"예방정비 권고 시점",
            value=f"{t_pm:.0f}시간",
            delta=f"약 {t_pm/24:.0f}일"
        )
    with col2:
        r_at_eta = np.exp(-1) * 100
        st.metric(
            label="η 시점 생존 확률",
            value=f"{r_at_eta:.1f}%",
            delta="β 무관 고정값"
        )
    with col3:
        f_at_pm = (1 - target_r/100) * 100
        st.metric(
            label="정비 시점 고장 확률",
            value=f"{f_at_pm:.1f}%",
            delta=f"목표 신뢰도 {target_r}% 기준"
        )

    # 신뢰도 곡선 그래프
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams['font.family'] = 'Malgun Gothic'

    t_range = np.linspace(1, eta_input * 2, 1000)
    R = np.exp(-(t_range/eta_input)**beta_input)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t_range, R*100, color='steelblue', linewidth=2, label='신뢰도 R(t)')
    ax.axhline(target_r, color='red', linestyle='--',
               label=f'목표 신뢰도 {target_r}%')
    ax.axvline(t_pm, color='orange', linestyle='--',
               label=f'예방정비 시점: {t_pm:.0f}h')
    ax.axvline(eta_input, color='purple', linestyle=':',
               label=f'η={eta_input}h (63.2% 고장)')
    ax.set_title(f'신뢰도 함수 R(t) — β={beta_input}, η={eta_input}h')
    ax.set_xlabel('운용 시간 (h)')
    ax.set_ylabel('생존 확률 (%)')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    # MTTR 단축 시나리오
    st.markdown("---")
    st.markdown("#### 목표 신뢰도별 예방정비 시점 비교")
    import pandas as pd
    scenarios = []
    for r in [99, 95, 90, 85, 80]:
        t = eta_input * (-np.log(r/100))**(1/beta_input)
        scenarios.append({
            "목표 신뢰도": f"{r}%",
            "예방정비 시점 (h)": f"{t:.0f}",
            "예방정비 주기 (일)": f"{t/24:.0f}",
            "예방정비 주기 (개월)": f"{t/24/30:.1f}"
        })
    st.dataframe(pd.DataFrame(scenarios), use_container_width=True)


with tab7:
    st.subheader("👥 인력 최적화 — 함정별 최적 인력 배분")
    st.caption("함정별 우선순위와 부서별 가용 인력을 입력하면 최적 배분을 자동 계산합니다.")

    import pulp

    st.markdown("#### 부서별 가용 인력 설정")
    col1, col2, col3 = st.columns(3)
    with col1:
        engine_crew = st.number_input("기관부 가용 인력 (명)", min_value=1, max_value=50, value=8)
    with col2:
        electric_crew = st.number_input("전자부 가용 인력 (명)", min_value=1, max_value=50, value=6)
    with col3:
        weapon_crew = st.number_input("무장부 가용 인력 (명)", min_value=1, max_value=50, value=4)

    st.markdown("---")
    st.markdown("#### 함정별 정보 입력")
    st.caption("담당 부서, 작전 우선순위(1~10), 일일 진도율, 최소 투입 인원을 입력하세요.")

    # 함정 데이터 입력 테이블
    dept_options = ["기관부", "전자부", "무장부"]

    ships = []
    for i in range(1, 6):
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        with col1:
            name = st.text_input(f"함정{i} 이름", value=f"함정{i}", key=f"name_{i}")
        with col2:
            dept = st.selectbox(f"담당부서", dept_options, key=f"dept_{i}")
        with col3:
            priority = st.number_input(f"우선순위", min_value=1, max_value=10,
                                       value=6-i, key=f"priority_{i}")
        with col4:
            rate = st.number_input(f"진도율(%)", min_value=1, max_value=20,
                                   value=5, key=f"rate_{i}")
        with col5:
            min_crew = st.number_input(f"최소인원", min_value=1, max_value=10,
                                       value=2, key=f"min_{i}")
        ships.append({
            "name": name, "dept": dept,
            "priority": priority, "rate": rate, "min_crew": min_crew
        })

    if st.button("🚀 최적 배분 계산", type="primary"):

        # 부서별 함정 분류
        engine_ships = [s for s in ships if s["dept"] == "기관부"]
        electric_ships = [s for s in ships if s["dept"] == "전자부"]
        weapon_ships = [s for s in ships if s["dept"] == "무장부"]

        # ILP 문제 정의
        prob = pulp.LpProblem("인력배분최적화", pulp.LpMinimize)

        # 결정변수 생성
        vars_dict = {}
        for s in ships:
            vars_dict[s["name"]] = pulp.LpVariable(
                s["name"], lowBound=s["min_crew"], cat='Integer'
            )

        # 목적함수: 가중 진도율 최대화
        prob += -pulp.lpSum([
            s["priority"] * s["rate"] * vars_dict[s["name"]]
            for s in ships
        ])

        # 부서별 인력 제약
        if engine_ships:
            prob += pulp.lpSum([vars_dict[s["name"]] for s in engine_ships]) <= engine_crew
        if electric_ships:
            prob += pulp.lpSum([vars_dict[s["name"]] for s in electric_ships]) <= electric_crew
        if weapon_ships:
            prob += pulp.lpSum([vars_dict[s["name"]] for s in weapon_ships]) <= weapon_crew

        # 풀기
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        if pulp.LpStatus[prob.status] == "Optimal":
            st.markdown("---")
            st.markdown("#### 최적 배분 결과")

            results = []
            total_weighted = 0
            for s in ships:
                crew = int(pulp.value(vars_dict[s["name"]]))
                days = 100 / (crew * s["rate"])
                weighted = s["priority"] * s["rate"] * crew
                total_weighted += weighted
                results.append({
                    "함정": s["name"],
                    "담당부서": s["dept"],
                    "우선순위": s["priority"],
                    "배치인력(명)": crew,
                    "완료예상(일)": f"{days:.1f}",
                    "가중진도율": weighted
                })

            import pandas as pd
            st.dataframe(pd.DataFrame(results), use_container_width=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 가중 진도율", f"{total_weighted:.0f}")
            with col2:
                total_crew = sum([int(pulp.value(vars_dict[s["name"]])) for s in ships])
                st.metric("총 투입 인력", f"{total_crew}명")
            with col3:
                st.metric("최적화 상태", pulp.LpStatus[prob.status])

            # 부서별 인력 사용 현황
            st.markdown("#### 부서별 인력 사용 현황")
            dept_usage = []
            for dept, capacity, dept_ships in [
                ("기관부", engine_crew, engine_ships),
                ("전자부", electric_crew, electric_ships),
                ("무장부", weapon_crew, weapon_ships)
            ]:
                if dept_ships:
                    used = sum([int(pulp.value(vars_dict[s["name"]])) for s in dept_ships])
                    dept_usage.append({
                        "부서": dept,
                        "가용인력": capacity,
                        "투입인력": used,
                        "여유인력": capacity - used,
                        "가동률": f"{used/capacity*100:.0f}%"
                    })
            st.dataframe(pd.DataFrame(dept_usage), use_container_width=True)

        else:
            st.error("최적해를 찾지 못했습니다. 인력 설정을 확인해주세요.")


with tab8:
    st.subheader("🔮 예측 정비 — 센서 데이터 이상 탐지")
    st.info("3단계 구현 예정 — 센서 데이터 입력 후 이상 탐지 및 고장 예측")