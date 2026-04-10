import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'

# ── 와이블 파라미터 설정 ──────────────────────────────────
# 수리창 시나리오: PKG-719 천안함 주기관
beta = 2.5    # 형상 모수: β > 1 → 마모기 (고장률 증가 중)
eta = 5000    # 척도 모수: 특성 수명 5,000시간

# ── 시간 범위 설정 ────────────────────────────────────────
t = np.linspace(1, 10000, 1000)  # 1~10,000시간

# ── 핵심 함수 계산 ────────────────────────────────────────
R = np.exp(-(t/eta)**beta)                      # 신뢰도 함수
F = 1 - R                                        # 누적 고장 확률
f = (beta/eta) * (t/eta)**(beta-1) * np.exp(-(t/eta)**beta)  # 확률밀도함수
lambda_t = (beta/eta) * (t/eta)**(beta-1)       # 순간 고장률

# ── 특정 시점 계산 ────────────────────────────────────────
check_times = [1000, 2000, 3000, 4000, 5000]
print("=== 주기관 와이블 분석 결과 ===")
print(f"β(베타): {beta}  →  마모기(IFR)")
print(f"η(에타): {eta}시간  →  특성 수명\n")
print(f"{'시간':>8} | {'R(t) 생존확률':>14} | {'F(t) 고장확률':>14} | {'λ(t) 순간고장률':>16}")
print("-" * 62)
for t_check in check_times:
    r = np.exp(-(t_check/eta)**beta)
    f_val = (beta/eta) * (t_check/eta)**(beta-1) * np.exp(-(t_check/eta)**beta)
    l = (beta/eta) * (t_check/eta)**(beta-1)
    print(f"{t_check:>8}h | {r*100:>13.1f}% | {(1-r)*100:>13.1f}% | {l:>16.6f}")

# ── 예방정비 최적 시점 계산 ───────────────────────────────
# 신뢰도 90% 유지 목표 → 고장 확률 10%가 되는 시점
target_reliability = 0.90
t_pm = eta * (-np.log(target_reliability))**(1/beta)
print(f"\n예방정비 권고 시점 (신뢰도 90% 유지): {t_pm:.0f}시간")
print(f"= 약 {t_pm/24:.0f}일 = 약 {t_pm/24/30:.1f}개월")

# ── 그래프 4개 ────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# R(t) 신뢰도 곡선
axes[0,0].plot(t, R*100, color='steelblue', linewidth=2)
axes[0,0].axhline(90, color='red', linestyle='--', label='목표 신뢰도 90%')
axes[0,0].axvline(t_pm, color='orange', linestyle='--',
                label=f'예방정비 시점: {t_pm:.0f}h')
axes[0,0].axvline(eta, color='purple', linestyle=':', label=f'η={eta}h')
axes[0,0].set_title('신뢰도 함수 R(t) — 생존 확률')
axes[0,0].set_xlabel('운용 시간 (h)')
axes[0,0].set_ylabel('생존 확률 (%)')
axes[0,0].legend(fontsize=9)
axes[0,0].grid(alpha=0.3)

# F(t) 누적 고장 확률
axes[0,1].plot(t, F*100, color='salmon', linewidth=2)
axes[0,1].axhline(63.2, color='purple', linestyle=':', label=f'F(η)=63.2% @ {eta}h')
axes[0,1].set_title('누적 고장 확률 F(t)')
axes[0,1].set_xlabel('운용 시간 (h)')
axes[0,1].set_ylabel('고장 확률 (%)')
axes[0,1].legend(fontsize=9)
axes[0,1].grid(alpha=0.3)

# f(t) 확률밀도함수
axes[1,0].plot(t, f, color='mediumseagreen', linewidth=2)
axes[1,0].set_title('확률밀도함수 f(t) — 고장 밀도')
axes[1,0].set_xlabel('운용 시간 (h)')
axes[1,0].set_ylabel('밀도')
axes[1,0].grid(alpha=0.3)

# λ(t) 순간 고장률
axes[1,1].plot(t, lambda_t*1000, color='darkorange', linewidth=2)
axes[1,1].axvline(t_pm, color='red', linestyle='--',
                label=f'예방정비 시점: {t_pm:.0f}h')
axes[1,1].set_title(f'순간 고장률 λ(t) — β={beta} (마모기)')
axes[1,1].set_xlabel('운용 시간 (h)')
axes[1,1].set_ylabel('고장률 (×10⁻³)')
axes[1,1].legend(fontsize=9)
axes[1,1].grid(alpha=0.3)

plt.suptitle(f'PKG-719 천안함 주기관 와이블 분석 (β={beta}, η={eta}h)', fontsize=13)
plt.tight_layout()
plt.savefig('weibull_result.png', dpi=150)
plt.show()
print("\n그래프가 weibull_result.png로 저장됐습니다.")