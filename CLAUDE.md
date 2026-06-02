# 🎯 AI 기반 기업 정량·정성 복합 리스크 검증 시스템

**Interactive Auditing & Compliance Verification Platform**

---

## 📋 프로젝트 개요

본 프로젝트는 **Open DART API**를 활용한 상장사 공시 정보 수집과 **Claude Haiku LLM** 기반의 경영진-감시자 청문회 시뮬레이션을 통해 기업의 재무 투명성과 잠재 리스크를 종합 분석하는 학회 발표 수준의 금융 분석 플랫폼입니다.

**핵심 데이터 흐름:**
```
Open DART API (정량 지표 + 주석)
    ↓
Financial Rule Engine (위험도 점수 산출)
    ↓
Claude Haiku LLM (경영진 소명 & 감시자 검증)
    ↓
Streamlit 3대 탭 UI (정량/청문/심층 분석 렌더링)
```

---

## 🏗️ 프로젝트 구조

```
ai-individual-project/
├── CLAUDE.md                 # 이 파일 (개발 가이드)
├── .gitignore               # Git 무시 파일 (.env, __pycache__ 등)
├── .env                      # API 키 (절대 커밋 금지)
├── requirements.txt          # 의존성 (dart-fss, langchain, streamlit 등)
├── app.py                    # 🎨 Streamlit 메인 UI + 렌더링
├── analyzer_pipeline.py      # 🧠 LangGraph 분석 엔진 (개발 참고용)
├── dart_test.py             # 🧪 DART API 테스트 스크립트
└── docs_cache/              # DART 캐시 폴더
```

---

## 🎯 3대 탭 레이아웃 (Critical Constraint)

```python
tab1, tab2, tab3 = st.tabs(["📊 정량 리스크 분석", "⚖️ 청문 공방 세션", "🔍 심층 주석 추적"])

with tab1:
    # 메트릭 카드 (종합 위험도, 매출질, 유동성, 부채)
    # + 상세 분석 결과 (불릿포인트)
    # + 기업 정보 & 리스크 평가 카드

with tab2:
    # 좌우 분할: st.columns([1, 1])
    # [좌] 👨‍💼 경영진 소명 (K-IFRS 기준 재무 건전성 입증)
    # [우] ⚠️ 감시자의 리스크 지적 (우발채무, 특수관계자 거래, 자산손상차손)

with tab3:
    # Node 3 리스크 아코디언 4개 확장
    # - 🚨 우발채무 및 계류 중인 소송
    # - 🤝 특수관계자 간 거래 및 자금 이동
    # - 📉 종속·관계기업 자산손상 및 투자 손실
    # - 💼 투자 권고 및 최종 결론
    # + 시스템 사용 주의사항 컨테이너
```

---

## 🎨 디자인 시스템 (에메랄드 테마)

### 색상 팔레트
```css
Primary: #1b4332 (딥 그린)
Secondary: #2d6a4f (포레스트 그린)
Accent: #40916c (세이지 그린)
Background: #f0f7f2 (소프트 그린)
Border: #c8e6c9 (라이트 그린)
Text: #1b3a2a (다크 그린)
```

### 필수 요소
- **폰트**: `Pretendard` 시스템 전체 강제 적용
- **히어로 배너**: 딥 그린 그라데이션 (`#1b4332` → `#2d6a4f`) + `border-radius: 24px`
- **분석 카드** (`.analysis-card`): 투명도 흰색 + `line-height: 1.9` + `padding: 24px`
- **섹션 헤더** (`.section-header`): 좌측 포인트 바 (`border-left: 4px solid #1b4332`)
- **데코 블롭**: `position: fixed` radial-gradient blur 효과
- **사이드바**: `backdrop-filter: blur(16px)` + `border-right: 1px solid #c8e6c9`
- **탭 액티브**: 언더라인 `3px solid #1b4332` + `font-weight: 600`

---

## 🚫 절대 규칙 (CRITICAL)

### Rule 1️⃣: 텍스트 떡짐 방지
**LLM 출력 마크다운이 HTML 내부에서 포매팅이 무시되는 문제 방지**

```python
# ❌ 절대 금지
st.html(f"<div>{llm_output}</div>")  # 줄바꿈, 불릿 무시됨

# ✅ 정규식 전처리 필수
def clean_markdown(text):
    """LLM 출력 전처리"""
    text = re.sub(r'【|】', '', text)  # 특수 괄호 제거
    text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)  # 마크다운 보존
    return text

mgmt_response = clean_markdown(mgmt_response)
st.markdown(mgmt_response)  # 마크다운 완전히 렌더링됨
```

### Rule 2️⃣: 상태 보존 (Session State)
**탭 및 아코디언 상호작용 시 데이터 휘발 방지**

```python
# 파이프라인 분리 원칙
if st.session_state.get("fetch_triggered", False):
    # [실행부] - 파이프라인 엔진 구동 (1회만)
    if "analysis_result" not in st.session_state:
        analysis = financial_rule_engine(financial_df)
        mgmt_response = management_explanations(...)
        caveats = stakeholder_caveats(...)
        st.session_state.analysis_result = {
            "analysis": analysis,
            "mgmt": mgmt_response,
            "caveats": caveats
        }
    
    # [렌더링부] - UI 출력 (반복 실행, 캐시된 데이터 사용)
    result = st.session_state.analysis_result
    tab1, tab2, tab3 = st.tabs([...])
    with tab1:
        st.metric("종합 위험도", result["analysis"]["financial_risk_score"])
```

### Rule 3️⃣: 보안 및 모델 지정
**API 키 하드코딩 금지 & 모델 고정**

```python
# ❌ 절대 금지
api_key = "sk-ant-v3-xxx..."  # 하드코딩

# ✅ 필수 방식
@st.cache_resource
def init_llm():
    api_key = os.getenv("Anthropic_API_KEY")
    return ChatAnthropic(
        api_key=api_key,
        model="claude-haiku-4-5-20251001",  # 2026년 최신 모델 고정
        temperature=0.7,
        max_tokens=1024
    )
```

**`.env` 파일 구조 (로컬만, 절대 커밋 금지)**
```
DART_API_KEY=xxxx
Anthropic_API_KEY=sk-ant-xxx
```

### Rule 4️⃣: 언어 규칙
- **UI 텍스트, 설명, 마크다운**: 한국어 필수
- **변수명, 함수명, 클래스명**: 영어 snake_case 필수
- **주석**: 한국어 가능하되 간결하게

```python
# ✅ 올바른 예
def extract_financial_statement(dart, corp_code: str) -> Optional[pd.DataFrame]:
    """재무제표 추출"""  # 한국어 주석
    ...

# ❌ 잘못된 예
def extract_financial_statement(dart, corp_code: str) -> Optional[pd.DataFrame]:
    """Extract financial statements"""  # 영어 주석 (불가)
```

---

## 🔧 핵심 함수 및 역할

### `app.py` - Streamlit UI + 렌더링
```python
financial_rule_engine()        # Node 1: 정량 위험도 점수 산출
management_explanations()      # Node 2: 경영진 소명 LLM 생성
stakeholder_caveats()          # Node 3: 감시자 검증 LLM 생성
extract_risk_categories()      # Node 3 파싱: 리스크 카테고리 추출
```

### DART API 함수
```python
search_company()               # 기업명 → 기업코드
get_periodic_report()          # 사업보고서 조회
extract_financial_statement()  # 재무제표 추출
extract_notes()                # 주석 텍스트 추출
find_account_value()           # 유연한 계정값 검색
```

---

## ⚡ 개발 흐름

### 1. 로컬 개발 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 (API 키 입력)
echo "DART_API_KEY=xxx" > .env
echo "Anthropic_API_KEY=sk-ant-xxx" >> .env

# Streamlit 실행
streamlit run app.py
```

### 2. 데이터 수집 흐름 (사이드바 → 메인)
```
[1] 기업명 입력 + "데이터 수집 시작" 클릭
    ↓
[2] DART API: 기업코드 검색
    ↓
[3] DART API: 최신 사업보고서 조회
    ↓
[4] DART API: 재무제표 추출
    ↓
[5] DART API: 주석 텍스트 추출
    ↓
[6] 분석 파이프라인 시작
```

### 3. 분석 파이프라인 흐름
```
[Node 1] financial_rule_engine()
├─ 매출 질 점수 (AR 회전율, OCF)
├─ 유동성 점수 (유동비율)
└─ 부채 점수 (부채비율)

[Node 2] management_explanations()
├─ 프롬프트: 정량 지표 + 재무제표 주석
├─ LLM: K-IFRS 기준 경영진 입장 생성
└─ 출력: Markdown (마크다운 완전 포맷)

[Node 3] stakeholder_caveats()
├─ 프롬프트: 경영진 소명 + 주석 전체
├─ LLM: 우발채무, 특수관계자, 자산손상 검증
└─ 출력: Markdown (마크다운 완전 포맷)

[Extract] extract_risk_categories()
└─ Node 3 파싱: 4개 아코디언 데이터 추출
```

### 4. UI 렌더링 흐름
```
[세션 초기화]
st.session_state.fetch_triggered = True

[탭 생성]
tab1, tab2, tab3 = st.tabs([...])

[Tab 1] 📊 정량 리스크 분석
├─ 메트릭 카드 (4열)
├─ 상세 분석 박스
└─ 기업 정보 & 리스크 종합 카드

[Tab 2] ⚖️ 청문 공방 세션
├─ st.columns([1, 1])
├─ [좌] 경영진 소명
└─ [우] 감시자 검증

[Tab 3] 🔍 심층 주석 추적
├─ 우발채무 아코디언
├─ 특수관계자 거래 아코디언
├─ 자산손상차손 아코디언
└─ 투자 권고 아코디언
```

---

## 🎮 치트키 & 명령어

### 일반 명령어
```bash
# 앱 실행
streamlit run app.py

# 종료
Ctrl + C

# 캐시 삭제 (강제 재렌더링)
rm -rf ~/.streamlit/cache
streamlit run app.py

# 특정 기업 분석 (사이드바에 입력)
"삼성전자" → 데이터 수집 시작
"하이브" → 데이터 수집 시작
```

### 디버깅 팁
```python
# 세션 상태 확인
st.write(st.session_state)

# LLM 출력 확인
st.write(mgmt_response)

# 재무 데이터 확인
st.dataframe(financial_df.head(10))

# 리스크 카테고리 파싱 확인
st.json(risk_categories)
```

### Git 워크플로우
```bash
# 변경사항 커밋 (.env 제외)
git add app.py analyzer_pipeline.py requirements.txt
git commit -m "fix: 텍스트 렌더링 개선"
git push origin main

# 커밋 이력 확인
git log --oneline -10
```

---

## 📐 아키텍처 원리

### 1. 탭 기반 정보 구조화
- **Tab 1**: 정량 데이터 (객관적 수치)
- **Tab 2**: 정성 데이터 (LLM 생성 텍스트)
- **Tab 3**: 심층 분석 (아코디언 구분)

각 탭은 **독립적인 `st.container(border=True)` 블록**으로 시각적으로 분리되어 가독성 극대화.

### 2. 좌우 비교 레이아웃 (Tab 2)
```python
col_left, col_right = st.columns([1, 1])

with col_left:
    st.container(border=True)  # 경영진 입장
    
with col_right:
    st.container(border=True)  # 감시자 입장
```

**의도**: 같은 높이에 비교 가능하도록 배치 → 대조 관점 강화

### 3. LLM 프롬프트 엔지니어링
- **Node 2** (경영진): 정량 지표 + 주석 발췌 → "K-IFRS 기준" 강조
- **Node 3** (감시자): 경영진 소명 + 전체 주석 → "리스크 추적" 강조
- **온도**: `temperature=0.7` (창의성 과도하지 않음)
- **토큰**: `max_tokens=1024` (적절한 길이)

### 4. 캐싱 전략
```python
@st.cache_resource  # API 초기화 (세션당 1회)
def init_dart_api(): ...

@st.cache_resource  # LLM 초기화 (세션당 1회)
def init_llm(): ...

# 분석 결과는 st.session_state에 보관 (휘발 방지)
```

---

## 🧪 테스트 & 검증

### 기능 검증 체크리스트
```
[ ] DART API: 기업 검색 정상
[ ] DART API: 공시 조회 정상
[ ] DART API: 재무제표 추출 정상
[ ] Financial Rule Engine: 점수 산출 정상
[ ] LLM (Node 2): 경영진 소명 생성 정상
[ ] LLM (Node 3): 감시자 검증 생성 정상
[ ] 마크다운 렌더링: 줄바꿈 & 불릿 정상
[ ] 탭 전환: 데이터 유지 정상
[ ] 아코디언 전개: 데이터 로드 정상
[ ] UI 반응성: 로딩 스피너 정상 (무한 로딩 없음)
```

### 시각적 검증
```
[ ] 색상: 그린 톤 일관성 확인
[ ] 폰트: Pretendard 적용 확인
[ ] 간격: 여백 적절한 정도 확인
[ ] 정렬: 카드/탭 정렬 정상 확인
[ ] 반응형: 모바일/태블릿 확인 (권장하지 않음)
```

---

## 🔗 외부 리소스

### DART API 문서
- [Open DART API 가이드](https://opendart.fss.or.kr)
- [dart-fss Python 패키지](https://github.com/FinanceData/OpenDartReader)

### Claude LLM
- [Claude API 문서](https://docs.anthropic.com)
- **모델**: `claude-haiku-4-5-20251001` (2026년 최신)

### Streamlit
- [Streamlit 문서](https://docs.streamlit.io)
- **주요 컴포넌트**: `st.tabs`, `st.columns`, `st.container`, `st.expander`

---

## 📞 문제 해결

### 문제: "The truth value of a Series is ambiguous"
**원인**: pandas Series를 `if not object:` 방식으로 체크
```python
# ❌ 원인
if not report:  # report가 Series일 때 에러

# ✅ 해결
if report is None:  # 명시적 None 체크
```

### 문제: LLM 출력이 HTML 내부에서 줄바꿈이 무시됨
**원인**: `st.html()` 내부에 직접 마크다운 삽입
```python
# ❌ 원인
st.html(f"<div>{llm_output}</div>")

# ✅ 해결
st.markdown(llm_output)  # Streamlit 마크다운 렌더러 사용
```

### 문제: 탭을 클릭하면 데이터가 재로드되거나 휘발됨
**원인**: 파이프라인 분석 결과가 세션 상태에 저장되지 않음
```python
# ✅ 해결
st.session_state.analysis_result = {
    "analysis": analysis,
    "mgmt": mgmt_response,
    "caveats": caveats
}
```

---

## 📝 커밋 메시지 규칙

```
feat: 새 기능 추가 (탭 구조 추가)
fix: 버그 수정 (텍스트 렌더링 개선)
refactor: 코드 구조 개선 (함수 분리)
docs: 문서 작성 (README 추가)
style: 스타일 개선 (CSS 업데이트)
perf: 성능 최적화 (캐싱 추가)
```

**예시**:
```
fix: 마크다운 렌더링 HTML 깨짐 현상 해결 및 세션 상태 보존 개선

- st.html() 대신 st.markdown() 사용
- Node 2, 3 출력을 st.session_state에 캐싱
- Tab 전환 시 데이터 휘발 방지
```

---

## 🎓 학습 리소스 & 개선 방향

### 현재 구현 수준
✅ 정량 분석 + 정성 LLM + UI 탭 구조 (완성)

### 향후 개선 방향 (Optional)
- [ ] 다중 기업 비교 분석
- [ ] 시계열 위험도 추이 차트
- [ ] PDF 리포트 자동 생성
- [ ] 실시간 공시 모니터링
- [ ] RAG 기반 주석 검색 고도화

---

**Last Updated: 2026-06-03**  
**Maintainer: Joo-Heejin (amyjoo22@g.skku.edu)**  
**License: MIT**
