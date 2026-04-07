import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'

# ── 시뮬레이션 설정 ───────────────────────────────────────
np.random.seed(42)
N = 10000

# ── MTBF와 MTTR을 삼각분포로 설정 ────────────────────────
# 고정값이 아닌 범위를 가진 확률 분포로 표현
MTBF = np.random.triangular(3000, 4380, 6000, N)  # 평균 고장 간격
MTTR = np.random.triangular(30, 44, 80, N)         # 평균 수리 시간

# ── 가용도 계산 ───────────────────────────────────────────
# A = MTBF / (MTBF + MTTR)
A = MTBF / (MTBF + MTTR)

# ── 결과 통계 출력 ────────────────────────────────────────
print("=== RAM + Monte Carlo 시뮬레이션 결과 ===")
print(f"평균 가용도:              {np.mean(A)*100:.2f}%")
print(f"최저 가용도:              {np.min(A)*100:.2f}%")
print(f"최고 가용도:              {np.max(A)*100:.2f}%")
print(f"표준편차:                 {np.std(A)*100:.2f}%p")
print()
print(f"가용도 99% 이상일 확률:   {np.mean(A >= 0.99)*100:.1f}%")
print(f"가용도 98% 이상일 확률:   {np.mean(A >= 0.98)*100:.1f}%")
print(f"가용도 95% 이상일 확률:   {np.mean(A >= 0.95)*100:.1f}%")
print()
print(f"50% 확률 가용도:          {np.percentile(A, 50)*100:.2f}%")
print(f"10% 확률 가용도 (하위):   {np.percentile(A, 10)*100:.2f}%")
print(f"5% 확률 가용도 (하위):    {np.percentile(A, 5)*100:.2f}%")

# ── 히스토그램 시각화 ─────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# MTBF 분포
axes[0].hist(MTBF, bins=50, color='steelblue', edgecolor='white', alpha=0.8)
axes[0].axvline(np.mean(MTBF), color='orange', linestyle='--',
                label=f'평균: {np.mean(MTBF):.0f}시간')
axes[0].set_title('MTBF 분포')
axes[0].set_xlabel('시간')
axes[0].set_ylabel('빈도')
axes[0].legend()

# MTTR 분포
axes[1].hist(MTTR, bins=50, color='salmon', edgecolor='white', alpha=0.8)
axes[1].axvline(np.mean(MTTR), color='orange', linestyle='--',
                label=f'평균: {np.mean(MTTR):.0f}시간')
axes[1].set_title('MTTR 분포')
axes[1].set_xlabel('시간')
axes[1].set_ylabel('빈도')
axes[1].legend()

# 가용도 분포
axes[2].hist(A * 100, bins=50, color='mediumseagreen', edgecolor='white', alpha=0.8)
axes[2].axvline(99, color='red', linestyle='--', linewidth=2, label='목표 가용도 99%')
axes[2].axvline(np.mean(A) * 100, color='orange', linestyle='--',
                label=f'평균: {np.mean(A)*100:.2f}%')
axes[2].set_title('가용도(A) 분포')
axes[2].set_xlabel('가용도 (%)')
axes[2].set_ylabel('빈도')
axes[2].legend()

plt.suptitle('PKG-719 천안함 주기관 RAM + Monte Carlo 시뮬레이션', fontsize=13)
plt.tight_layout()
plt.savefig('ram_montecarlo_result.png', dpi=150)
plt.show()
print("\n그래프가 ram_montecarlo_result.png로 저장됐습니다.")