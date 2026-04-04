import pandas as pd

# ── 1. 데이터 불러오기 ────────────────────────────────────
df_process = pd.read_csv("data/공정스케줄.csv")
df_stock = pd.read_csv("data/자재재고.csv")

# ── 2. 날짜 컬럼을 날짜 타입으로 변환 ────────────────────
# 문자열로 읽힌 날짜를 계산 가능한 형태로 바꿈
date_cols = ["계획시작일", "계획종료일", "실제시작일", "실제종료일"]
for col in date_cols:
    df_process[col] = pd.to_datetime(df_process[col])

# ── 3. 결측치 확인 (실제종료일이 없는 = 진행중 작업) ─────
print("=== 결측치 현황 ===")
print(df_process.isnull().sum())

# ── 4. EVM 계산: 공정 달성률(SPI) ────────────────────────
# SPI = 실적공수 / 계획공수
# SPI > 1.0 : 계획보다 빠름 / SPI < 1.0 : 계획보다 느림(지연)
df_process["SPI"] = df_process["실적공수"] / df_process["계획공수"]

print("\n=== EVM 공정 달성률 (SPI) ===")
print(df_process[["작업명", "담당부서", "계획공수", "실적공수", "SPI"]])

# ── 5. 지연 작업 필터링 ───────────────────────────────────
delayed = df_process[df_process["SPI"] < 1.0]
print(f"\n⚠️ 지연 작업 수: {len(delayed)}건")
print(delayed[["작업명", "담당부서", "SPI"]])

# ── 6. ROP 계산: 재고 부족 품목 ──────────────────────────
# ROP = 일평균사용량 × 조달기간 + 안전재고
# 현재고 < ROP 이면 즉시 발주 필요
df_stock["ROP계산값"] = (
    df_stock["일평균사용량"] * df_stock["조달기간(일)"] + df_stock["안전재고"]
)
df_stock["발주필요"] = df_stock["현재고"] < df_stock["ROP계산값"]

print("\n=== ROP 재고 현황 ===")
print(df_stock[["품목명", "현재고", "ROP계산값", "발주필요"]])

shortage = df_stock[df_stock["발주필요"] == True]
print(f"\n🚨 즉시 발주 필요 품목: {len(shortage)}건")
print(shortage[["품목명", "현재고", "ROP계산값"]])