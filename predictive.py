import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.linear_model import LinearRegression

matplotlib.rcParams['font.family'] = 'Malgun Gothic'

# ── 1. 가상 센서 데이터 생성 ──────────────────────────────
np.random.seed(42)
days = 120

# 세 가지 요소 합성
trend = np.linspace(2.0, 3.5, days)                          # 추세: 서서히 증가
seasonality = 0.3 * np.sin(2 * np.pi * np.arange(days) / 30) # 계절성: 30일 주기
noise = np.random.normal(0, 0.1, days)                        # 잔차: 랜덤 노이즈
vibration = trend + seasonality + noise

# 마지막 20일: 고장 징후 추가 (급격한 상승)
vibration[-20:] += np.linspace(0, 1.5, 20)

# 날짜 인덱스 생성
dates = pd.date_range(start='2026-01-01', periods=days, freq='D')
df = pd.DataFrame({'날짜': dates, '진동값': vibration})

print("=== PKG-719 천안함 주기관 진동 데이터 분석 ===\n")
print(f"분석 기간: {dates[0].date()} ~ {dates[-1].date()}")
print(f"전체 데이터: {days}일")
print(f"평균 진동값: {np.mean(vibration):.3f} mm/s")
print(f"최대 진동값: {np.max(vibration):.3f} mm/s")
print(f"최소 진동값: {np.min(vibration):.3f} mm/s\n")

# ── 2. 시계열 분해 ────────────────────────────────────────
result = seasonal_decompose(vibration, model='additive', period=30)

# ── 3. 이상 탐지 — 3-시그마 규칙 ─────────────────────────
# 정상 구간(1~100일) 기준으로 상한선 설정
normal_period = vibration[:100]
mean_normal = np.mean(normal_period)
std_normal = np.std(normal_period)
upper_limit = mean_normal + 3 * std_normal  # 3-시그마 상한선

# 이상값 탐지
anomalies = df[df['진동값'] > upper_limit]

print("=== 이상 탐지 결과 (3-시그마 규칙) ===")
print(f"정상 구간 평균: {mean_normal:.3f} mm/s")
print(f"정상 구간 표준편차: {std_normal:.3f} mm/s")
print(f"이상 탐지 상한선: {upper_limit:.3f} mm/s")
print(f"이상값 탐지: {len(anomalies)}건\n")

if len(anomalies) > 0:
    print("이상값 발생 날짜:")
    for _, row in anomalies.iterrows():
        print(f"  {row['날짜'].date()} → 진동값 {row['진동값']:.3f} mm/s "
              f"(상한선 대비 +{row['진동값']-upper_limit:.3f})")

# ── 4. 선형 추세 예측 ─────────────────────────────────────
# 최근 30일 데이터로 추세선 학습
recent_days = 30
X_train = np.arange(days - recent_days, days).reshape(-1, 1)
y_train = vibration[days - recent_days:]

model = LinearRegression()
model.fit(X_train, y_train)

# 향후 30일 예측
future_x = np.arange(days, days + 30).reshape(-1, 1)
future_pred = model.predict(future_x)
future_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1),
                              periods=30, freq='D')

# 경보 임계값 도달 시점 계산
warning_threshold = 5.0  # 경보 임계값 5.0 mm/s
exceed_idx = np.where(future_pred >= warning_threshold)[0]

print(f"\n=== 추세 예측 결과 (향후 30일) ===")
print(f"경보 임계값: {warning_threshold} mm/s")
if len(exceed_idx) > 0:
    exceed_date = future_dates[exceed_idx[0]]
    print(f"🚨 경보 임계값 도달 예상일: {exceed_date.date()}")
    print(f"   현재로부터 {exceed_idx[0]+1}일 후")
else:
    print("✅ 향후 30일 내 경보 임계값 도달 없음")
    print(f"   30일 후 예측 진동값: {future_pred[-1]:.3f} mm/s")

# ── 5. 그래프 4개 ─────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 전체 진동 데이터 + 이상 탐지
axes[0,0].plot(dates, vibration, color='steelblue',
               linewidth=1.5, label='진동값')
axes[0,0].axhline(upper_limit, color='red', linestyle='--',
                  linewidth=1.5, label=f'3σ 상한선: {upper_limit:.2f}')
axes[0,0].scatter(anomalies['날짜'], anomalies['진동값'],
                  color='red', zorder=5, s=50, label=f'이상값 {len(anomalies)}건')
axes[0,0].set_title('진동 데이터 + 이상 탐지')
axes[0,0].set_xlabel('날짜')
axes[0,0].set_ylabel('진동값 (mm/s)')
axes[0,0].legend(fontsize=9)
axes[0,0].grid(alpha=0.3)

# 시계열 분해 — 추세
axes[0,1].plot(dates, result.trend, color='darkorange', linewidth=2)
axes[0,1].set_title('추세(Trend) 분해')
axes[0,1].set_xlabel('날짜')
axes[0,1].set_ylabel('추세값')
axes[0,1].grid(alpha=0.3)

# 시계열 분해 — 계절성
axes[1,0].plot(dates, result.seasonal, color='mediumseagreen', linewidth=1.5)
axes[1,0].set_title('계절성(Seasonality) 분해')
axes[1,0].set_xlabel('날짜')
axes[1,0].set_ylabel('계절성값')
axes[1,0].grid(alpha=0.3)

# 추세 예측
axes[1,1].plot(dates[-recent_days:], y_train,
               color='steelblue', linewidth=1.5, label='최근 30일 실측')
axes[1,1].plot(future_dates, future_pred,
               color='red', linewidth=2, linestyle='--', label='향후 30일 예측')
axes[1,1].axhline(warning_threshold, color='darkred', linestyle=':',
                  linewidth=1.5, label=f'경보 임계값: {warning_threshold}')
if len(exceed_idx) > 0:
    axes[1,1].axvline(future_dates[exceed_idx[0]], color='red',
                      linestyle='--', alpha=0.7)
axes[1,1].set_title('선형 추세 예측 (향후 30일)')
axes[1,1].set_xlabel('날짜')
axes[1,1].set_ylabel('진동값 (mm/s)')
axes[1,1].legend(fontsize=9)
axes[1,1].grid(alpha=0.3)

plt.suptitle('PKG-719 천안함 주기관 예측 정비 분석', fontsize=13)
plt.tight_layout()
plt.savefig('predictive_result.png', dpi=150)
plt.show()
print("\n그래프가 predictive_result.png로 저장됐습니다.")

# ── 6. 이동 평균 기반 이상 탐지 ──────────────────────────
from sklearn.ensemble import IsolationForest

window = 14  # 14일 이동 평균

# 이동 평균과 이동 표준편차 계산
rolling_mean = pd.Series(vibration).rolling(window=window).mean()
rolling_std = pd.Series(vibration).rolling(window=window).std()

# 이동 상한선/하한선
rolling_upper = rolling_mean + 3 * rolling_std
rolling_lower = rolling_mean - 3 * rolling_std

# 이동 평균 기반 이상값 탐지
anomaly_rolling = (vibration > rolling_upper) | (vibration < rolling_lower)
anomaly_rolling_dates = dates[anomaly_rolling]

print("\n=== 이동 평균 기반 이상 탐지 결과 ===")
print(f"이동 평균 기간: {window}일")
print(f"이상값 탐지: {anomaly_rolling.sum()}건")

# ── 7. Isolation Forest 기반 이상 탐지 ───────────────────
# ML 기반 이상 탐지: 데이터 패턴을 학습해서 이상값 자동 식별
# contamination: 전체 데이터 중 이상값 비율 예상치
iso_forest = IsolationForest(contamination=0.05, random_state=42)

# 진동값을 2D 배열로 변환 (sklearn 입력 형식)
X = vibration.reshape(-1, 1)
predictions = iso_forest.fit_predict(X)

# -1: 이상값, 1: 정상값
anomaly_iso = predictions == -1
anomaly_iso_dates = dates[anomaly_iso]

print(f"\n=== Isolation Forest 이상 탐지 결과 ===")
print(f"탐지된 이상값: {anomaly_iso.sum()}건")
print("이상값 발생 날짜:")
for d, v in zip(anomaly_iso_dates, vibration[anomaly_iso]):
    print(f"  {d.date()} → 진동값 {v:.3f} mm/s")

# ── 8. 비교 그래프 ────────────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(15, 5))

# 이동 평균 기반
axes2[0].plot(dates, vibration, color='steelblue',
              linewidth=1.5, alpha=0.7, label='진동값')
axes2[0].plot(dates, rolling_mean, color='orange',
              linewidth=2, label=f'{window}일 이동 평균')
axes2[0].fill_between(dates, rolling_lower, rolling_upper,
                       alpha=0.2, color='orange', label='정상 범위 (±3σ)')
axes2[0].scatter(anomaly_rolling_dates, vibration[anomaly_rolling],
                 color='red', zorder=5, s=50,
                 label=f'이상값 {anomaly_rolling.sum()}건')
axes2[0].set_title(f'이동 평균 기반 이상 탐지 ({window}일 윈도우)')
axes2[0].set_xlabel('날짜')
axes2[0].set_ylabel('진동값 (mm/s)')
axes2[0].legend(fontsize=9)
axes2[0].grid(alpha=0.3)

# Isolation Forest 기반
axes2[1].scatter(dates[~anomaly_iso], vibration[~anomaly_iso],
                 color='steelblue', s=20, alpha=0.7, label='정상')
axes2[1].scatter(anomaly_iso_dates, vibration[anomaly_iso],
                 color='red', s=50, zorder=5,
                 label=f'이상값 {anomaly_iso.sum()}건')
axes2[1].set_title('Isolation Forest 이상 탐지 (ML 기반)')
axes2[1].set_xlabel('날짜')
axes2[1].set_ylabel('진동값 (mm/s)')
axes2[1].legend(fontsize=9)
axes2[1].grid(alpha=0.3)

plt.suptitle('이상 탐지 방법 비교: 이동 평균 vs Isolation Forest', fontsize=13)
plt.tight_layout()
plt.savefig('anomaly_detection.png', dpi=150)
plt.show()
print("\n그래프가 anomaly_detection.png로 저장됐습니다.")