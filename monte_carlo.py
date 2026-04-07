import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트 설정

# ── 시뮬레이션 설정 ───────────────────────────────────────
np.random.seed(42)          # 재현 가능한 결과를 위한 시드 고정
N = 10000                   # 시뮬레이션 반복 횟수

# ── 삼각분포로 각 작업 기간 설정 (최소, 최빈, 최대) ─────
# 형식: np.random.triangular(최소, 최빈, 최대, 반복횟수)
A = np.random.triangular(1, 2, 3, N)      # 입거 및 초기점검
B = np.random.triangular(4, 5, 8, N)      # 주기관 분해
C = np.random.triangular(6, 8, 15, N)     # 부품 조달 (불확실성 큼)
D = np.random.triangular(3, 4, 6, N)      # 주기관 재조립
E = np.random.triangular(2, 3, 5, N)      # 추진축 분해
F = np.random.triangular(5, 6, 9, N)      # 추진축 베어링 교체
G = np.random.triangular(1, 2, 3, N)      # 추진축 재조립
H = np.random.triangular(2, 3, 4, N)      # 시운전 및 최종점검

# ── Critical Path 계산: A → B → C → D → G → H ───────────
# G는 D와 F 중 늦게 끝나는 것에 종속
path_main = A + B + C + D                 # 주기관 라인
path_sub = A + E + F                      # 추진축 라인
G_start = np.maximum(path_main, path_sub) # G는 두 라인 중 늦은 것 기다림
total_days = G_start + G + H              # 전체 공기

# ── 결과 통계 출력 ────────────────────────────────────────
print("=== Monte Carlo 시뮬레이션 결과 ===")
print(f"평균 완료일:         {np.mean(total_days):.1f}일")
print(f"표준편차:            {np.std(total_days):.1f}일")
print(f"최단 완료일:         {np.min(total_days):.1f}일")
print(f"최장 완료일:         {np.max(total_days):.1f}일")
print(f"50% 확률 완료일:     {np.percentile(total_days, 50):.1f}일")
print(f"80% 확률 완료일:     {np.percentile(total_days, 80):.1f}일")
print(f"90% 확률 완료일:     {np.percentile(total_days, 90):.1f}일")
print(f"95% 확률 완료일:     {np.percentile(total_days, 95):.1f}일")

# ── 히스토그램 시각화 ─────────────────────────────────────
plt.figure(figsize=(10, 6))
plt.hist(total_days, bins=50, color='steelblue', edgecolor='white', alpha=0.8)

# 90% 기준선 표시
p90 = np.percentile(total_days, 90)
plt.axvline(p90, color='red', linestyle='--', linewidth=2,
            label=f'90% 확률 완료: {p90:.1f}일')

# 평균선 표시
plt.axvline(np.mean(total_days), color='orange', linestyle='--', linewidth=2,
            label=f'평균: {np.mean(total_days):.1f}일')

plt.title('PKG-719 천안함 수리 기간 Monte Carlo 시뮬레이션 (10,000회)')
plt.xlabel('총 수리 기간 (일)')
plt.ylabel('빈도')
plt.legend()
plt.tight_layout()
plt.savefig('monte_carlo_result.png', dpi=150)
plt.show()
print("\n그래프가 monte_carlo_result.png로 저장됐습니다.")