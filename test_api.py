import os
from dotenv import load_dotenv
import anthropic

# ── .env 파일에서 API 키 불러오기 ─────────────────────────
load_dotenv()

# ── Anthropic 클라이언트 초기화 ───────────────────────────
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── 테스트용 공정 데이터 (나중에 실제 DataFrame으로 교체) ──
test_data = """
[공정 지연 현황]
- 레이더 시스템 점검 (전자부): SPI 0.95 → 5% 지연
- 함포 유압계통 정비 (무장부): SPI 0.70 → 30% 지연
- 선체 도장 작업 (선체부): SPI 0.45 → 55% 지연

[재고 부족 현황]
- 주기관 오일필터: 현재고 12개, ROP 34개 → 즉시 발주 필요
- 추진축 베어링: 현재고 3개, ROP 12개 → 즉시 발주 필요
"""

# ── Claude에게 브리핑 요청 ────────────────────────────────
message = client.messages.create(
    model="claude-sonnet-4-5",       # Claude Sonnet 4.6 최신 모델
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"""당신은 함정 수리창의 MRO 관제 AI입니다.
아래 데이터를 분석하여 수리창 담당자에게 브리핑하세요.
우선순위가 높은 순서로 3가지 조치사항을 간결하게 제시하세요.

{test_data}"""
        }
    ]
)

print("=== Claude AI 브리핑 ===")
print(message.content[0].text)