# AI 기반 기업 정량·정성 복합 리스크 검증 시스템

> **🇰🇷 필수: 이 프로젝트의 모든 응답과 설명은 반드시 한국어로 해주세요.**
> 코드 변수명·함수명은 영어 snake_case, UI 텍스트와 모든 설명은 한국어.

---

## 처음 시작하는 분들께 — 이 문장들을 채팅창에 그대로 입력하세요

**📌 첫 번째 — 프로젝트 현황 파악:**
```
이 프로젝트가 어떻게 구성되어 있는지 한국어로 설명해줘. 내가 진행 중인 AI 기반 기업 정량·정성 복합 리스크 검증 시스템의 현황을 정리해줘.
```

**📌 두 번째 — 앱 실행:**
```
requirements.txt 설치하고 streamlit run app.py 실행해줘.
```

**📌 세 번째 — 파일 올릴 때 (push):**
```
내 코드를 GitHub에 올려줘. push 전에 git pull --rebase origin main 먼저 실행해줘.
```

**📌 막혔을 때:**
```
[에러 메시지 붙여넣기] 이 에러 해결해줘.
```

---

## 프로젝트 구조

**데이터 흐름:**
```
기업 재무 데이터 (DART API)
  ↓
정량 위험도 분석 (Financial Rule Engine)
  - 매출 변동성 (40%)
  - 유동성 지표 (35%)
  - 부채 비율 (25%)
  ↓
정성 크로스체킹 (Claude Haiku LLM)
  - 정량 점수 재검증
  - 정성 적절성 평가
  - 최종 등급 산출 (HIGH/MEDIUM/LOW)
  ↓
시나리오 스트레스 테스트 (4가지 위기 시나리오)
  ↓
Streamlit 4대 탭 UI 렌더링
```

**파일 구조:**
```
app.py                  # Streamlit UI (main)
analyzer_pipeline.py    # LangGraph 분석 엔진
requirements.txt        # 의존성
.env                    # API 키 (절대 커밋 금지)
CLAUDE.md              # 이 파일
```

---

## 기술 스택

- **언어:** Python 3.11
- **백엔드:** LangGraph, Claude API (claude-haiku-4-5-20251001)
- **데이터:** DART-FSS API, Pandas, NumPy
- **UI:** Streamlit, Plotly (차트)
- **환경:** .env 기반 API 키 관리

---

## 환경 변수 (.env 파일에만, 절대 코드에 직접 X)

**중요:** `.env` 파일은 git에 커밋하지 않음 (`.gitignore`에 추가됨)

---

## 절대 규칙

1. **API 키 하드코딩 금지:** .env 파일에서만 불러오기
   ```python
   # ❌ 금지: api_key = "sk-ant-xxx"
   # ✅ 필수: api_key = os.getenv("ANTHROPIC_API_KEY")
   ```

2. **모델 잠금:** `claude-haiku-4-5-20251001`만 사용
   ```python
   # ✅ 필수: model="claude-haiku-4-5-20251001"
   ```

3. **세션 상태 캐싱:** 데이터 휘발 방지
   ```python
   if "analysis_result" not in st.session_state:
       st.session_state.analysis_result = result
   ```

4. **마크다운 렌더링:** st.markdown() 사용 (st.html() 금지)
   ```python
   # ❌ 금지: st.html(f"<div>{output}</div>")
   # ✅ 필수: st.markdown(output)
   ```

5. **언어:** UI 텍스트는 한국어, 변수명은 영어 snake_case

---

## 4주 일정

| 주차 | 목표 | 상태 |
|---|---|---|
| 1주차 | 환경 설정 + DART API 연결 | ✅ 완료 |
| 2주차 | 정량 분석 + 가중치 통합 | ✅ 완료 |
| 3주차 | 정성 검증 + 최종 등급 | ✅ 완료 |
| 4주차 | 시나리오 분석 + 5년 추세 + UI 완성 | ✅ 완료 (95%) |

---

## 에러가 났을 때 — 개선 루프

에러는 시스템을 더 강하게 만들 기회입니다. 두려워하지 마세요.

1. **파악** — 에러 메시지 전체를 읽는다
2. **붙여넣기** — Claude 채팅창에 에러 메시지 그대로 붙여넣기
3. **수정** — Claude가 제안한 수정을 적용한다
4. **확인** — 실제로 작동하는지 확인한다
5. **계속** — 더 강해진 코드로 다음 단계로

> 에러 메시지는 Claude의 입력값입니다. 에러가 날수록 코드가 단단해집니다.

---

## 아키텍처 원리

**왜 DART API를 코드 스크립트로 짜는가**

AI가 모든 걸 직접 처리하려 하면 정확도가 빠르게 떨어집니다.
각 단계의 정확도가 90%라면 → 5단계 후 전체 정확도는 59%로 떨어집니다.

**우리 프로젝트는:**
- **DART API 호출, 재무 지표 계산** → Python 스크립트 (결정론적, 항상 같은 결과)
- **정성 검증, 판단, 평가** → Claude API (claude-haiku-4-5-20251001)
- **최종 통합 & 등급 산출** → 규칙 기반 엔진

Claude는 판단에 집중하고, 반복 실행은 코드 스크립트에 맡깁니다.
이것이 PoC 프로젝트 아키텍처의 핵심 원리입니다.

---

**Last Updated: 2026-06-24**
