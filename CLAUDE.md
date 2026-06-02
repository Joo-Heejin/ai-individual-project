# 🎯 AI 기반 기업 정량·정성 복합 리스크 검증 시스템

**Interactive Auditing & Compliance Verification Platform**

---

## 📋 프로젝트 개요

Open DART API 정량 지표 → Financial Rule Engine → Claude Haiku LLM 청문 공방 → Streamlit 3대 탭 UI

**파일 구조:**
```
app.py                   # Streamlit UI + 렌더링 (main)
analyzer_pipeline.py     # LangGraph 분석 엔진 (참고용)
CLAUDE.md               # 이 파일
requirements.txt        # 의존성
.env                    # API 키 (절대 커밋 금지)
```

---

## 🎯 3대 탭 레이아웃 (필수 제약)

```python
tab1, tab2, tab3 = st.tabs(["📊 정량 리스크 분석", "⚖️ 청문 공방 세션", "🔍 심층 주석 추적"])

# Tab 1: 메트릭 + 상세 분석 + 기업 정보 카드
# Tab 2: st.columns([1,1]) 좌우 분할 → [경영진 소명] vs [감시자 검증]
# Tab 3: 우발채무 / 특수관계자 거래 / 자산손상차손 / 투자 권고 아코디언
```

---

## 🚫 절대 규칙 4가지

### Rule 1: 텍스트 떡짐 방지
```python
# ❌ 금지: st.html(f"<div>{llm_output}</div>")
# ✅ 필수: st.markdown(mgmt_response)  # 마크다운 완전 렌더링
```

### Rule 2: 상태 보존 (Session State)
```python
# 파이프라인 분리: 실행부 (1회) / 렌더링부 (반복)
if "analysis_result" not in st.session_state:
    result = {분석 결과}
    st.session_state.analysis_result = result
```

### Rule 3: 보안 & 모델
```python
# ❌ 금지: api_key = "sk-ant-xxx"
# ✅ 필수: api_key = os.getenv("Anthropic_API_KEY")
# 모델 고정: "claude-haiku-4-5-20251001" (2026년)
```

### Rule 4: 언어
- UI 텍스트 & 설명: 한국어
- 변수/함수명: 영어 snake_case

---

## 🎨 디자인 시스템 (에메랄드 테마)

```css
Primary: #1b4332 (딥 그린)
Secondary: #2d6a4f (포레스트)
Background: #f0f7f2 (소프트 그린)
Border: #c8e6c9 (라이트)
```

**필수 요소:**
- 폰트: `Pretendard` 전역 강제
- 히어로 배너: 딥 그린 그라데이션 + `border-radius: 24px`
- 분석 카드: 투명 흰색 + `line-height: 1.9`
- 섹션 헤더: 좌측 포인트 바 (`border-left: 4px`)
- 데코: `position: fixed` radial-gradient blur

---

## 🔧 핵심 함수

```python
financial_rule_engine()        # Node 1: 정량 위험도 점수
management_explanations()      # Node 2: 경영진 소명
stakeholder_caveats()          # Node 3: 감시자 검증
extract_risk_categories()      # Node 3 파싱: 아코디언 데이터
```

---

## ⚡ 개발 명령어

```bash
streamlit run app.py           # 앱 실행
git add app.py && git commit -m "fix: ..."  # 커밋
git push origin main           # 푸시
```

---

## 🧪 문제 해결

**Series boolean 에러:**
```python
# ❌ if not report:
# ✅ if report is None:
```

**탭 데이터 휘발:**
→ `st.session_state` 캐싱 필수

**마크다운 무시:**
→ `st.markdown()` 대신 `st.html()` 금지

---

## 📞 커밋 메시지 규칙

```
feat: 새 기능 (ex: 탭 구조 추가)
fix: 버그 수정 (ex: 텍스트 렌더링)
refactor: 코드 정리
docs: 문서 (ex: CLAUDE.md)
```

---

**Last Updated: 2026-06-03**
