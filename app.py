# -*- coding: utf-8 -*-
"""
이해관계자 관점의 기업 리스크 탐지 시스템 - 웹 인터페이스
(Stakeholder-Perspective Enterprise Risk Detection System - Web Interface)

학회 발표용 전문 금융·회계 분석 플랫폼
"""

import os
import sys
import re
from typing import TypedDict, Optional, Tuple
import streamlit as st
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_anthropic import ChatAnthropic
import OpenDartReader
import pandas as pd
from datetime import datetime

# UTF-8 설정
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(".env")

# ============================================================================
# Streamlit 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="Enterprise Risk Detection System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    body {
        background: linear-gradient(135deg, #f0f7f2 0%, #e8f5e9 100%);
        color: #1b3a2a;
    }

    /* 데코 블롭 효과 */
    .deco-blob-1 {
        position: fixed;
        top: -50px;
        right: -100px;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(45, 106, 79, 0.08) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(60px);
        z-index: -1;
        pointer-events: none;
    }

    .deco-blob-2 {
        position: fixed;
        bottom: -100px;
        left: -100px;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(27, 67, 50, 0.06) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(80px);
        z-index: -1;
        pointer-events: none;
    }

    /* 히어로 배너 */
    .hero-banner {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
        color: white;
        padding: 40px 30px;
        border-radius: 24px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(27, 67, 50, 0.15);
        text-align: center;
    }

    .hero-banner h1 {
        font-size: 2.2em;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-banner p {
        font-size: 1.1em;
        margin: 12px 0 0 0;
        opacity: 0.95;
        font-weight: 400;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: rgba(232, 245, 233, 0.7) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid #c8e6c9;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #a5d6a7;
    }

    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #1b4332 !important;
        color: #1b4332 !important;
        font-weight: 600;
    }

    .stTabs [aria-selected="false"] {
        color: #558b63;
        font-weight: 500;
    }

    /* 분석 카드 */
    .analysis-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #c8e6c9;
        margin: 16px 0;
        box-shadow: 0 4px 16px rgba(27, 67, 50, 0.08);
        line-height: 1.9;
        backdrop-filter: blur(10px);
    }

    /* 섹션 헤더 */
    .section-header {
        border-left: 4px solid #1b4332;
        padding-left: 16px;
        margin: 24px 0 16px 0;
        font-weight: 600;
        color: #1b4332;
    }

    /* 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2);
    }

    /* 컨테이너 스타일 */
    [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
        border-radius: 16px;
    }

    /* 위험도 색상 */
    .risk-high {
        color: #c41c3b;
        font-weight: 700;
    }

    .risk-normal {
        color: #2e7d32;
        font-weight: 700;
    }

    .risk-caution {
        color: #f57c00;
        font-weight: 700;
    }

    /* 아코디언 스타일 */
    [data-testid="stExpander"] {
        border: 1px solid #a5d6a7 !important;
        border-radius: 12px !important;
        background: rgba(232, 245, 233, 0.3) !important;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
    }

    /* 성공/경고 메시지 */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #2e7d32;
    }

    .stWarning {
        background: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #f57c00;
    }

    .stError {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #c41c3b;
    }

    /* 정보 박스 */
    .stInfo {
        background: rgba(45, 106, 79, 0.05);
        border-left: 4px solid #40916c;
    }

    /* 마크다운 링크 */
    a {
        color: #2d6a4f !important;
        text-decoration: none;
        font-weight: 500;
    }

    a:hover {
        color: #1b4332 !important;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# 데코 블롭 요소 추가
st.html("""
<div class="deco-blob-1"></div>
<div class="deco-blob-2"></div>
""")

# ============================================================================
# 초기화: DART API, LLM, 캐시
# ============================================================================

@st.cache_resource
def init_dart_api():
    """DART API 초기화"""
    dart_api_key = os.getenv("DART_API_KEY")
    if not dart_api_key:
        st.error("❌ DART_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
        st.stop()

    try:
        dart = OpenDartReader(dart_api_key)
        return dart
    except Exception as e:
        st.error(f"❌ DART API 초기화 실패: {e}")
        st.stop()

@st.cache_resource
def init_llm():
    """Claude LLM 초기화 (Haiku 모델)"""
    api_key = os.getenv("Anthropic_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
        st.stop()

    return ChatAnthropic(
        api_key=api_key,
        model="claude-haiku-4-5-20251001",
        temperature=0.7,
        max_tokens=1024
    )

dart = init_dart_api()
llm = init_llm()

# ============================================================================
# DART 데이터 수집 함수
# ============================================================================

def search_company(dart, company_name: str) -> Tuple[Optional[str], Optional[str]]:
    """기업명으로 검색"""
    try:
        results = dart.company_by_name(company_name)
        if not results:
            return None, None

        corp_info = None
        for result in results:
            if result.get('corp_cls') == 'Y':
                corp_info = result
                break

        if not corp_info:
            corp_info = results[0]

        return corp_info['corp_code'], corp_info['corp_name']
    except:
        return None, None

def get_periodic_report(dart, corp_code: str, corp_name: str) -> Tuple[Optional[pd.Series], Optional[str]]:
    """정기 공시 조회"""
    try:
        all_filings = dart.list(corp=corp_code)
        if all_filings.empty:
            return None, None

        business_reports = all_filings[
            all_filings['report_nm'].str.contains('사업보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        if not business_reports.empty:
            return business_reports.iloc[0], '사업보고서'

        semi_reports = all_filings[
            all_filings['report_nm'].str.contains('반기보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        if not semi_reports.empty:
            return semi_reports.iloc[0], '반기보고서'

        return None, None
    except:
        return None, None

def extract_financial_statement(dart, corp_code: str) -> Optional[pd.DataFrame]:
    """재무제표 추출"""
    try:
        current_year = datetime.now().year
        fs_data = None

        for year in [current_year, current_year - 1, current_year - 2]:
            try:
                fs_data = dart.finstate_all(corp_code, str(year))
                if fs_data is not None and not fs_data.empty:
                    return fs_data
            except:
                continue

        return None
    except:
        return None

def extract_notes(dart, rcept_no: str) -> Optional[str]:
    """주석 추출"""
    try:
        doc_xml = dart.document(rcept_no)
        if not doc_xml:
            return None

        p_tags = re.findall(r'<P[^>]*>([^<]+)</P>', doc_xml)
        text = ' '.join(p_tags)
        text = re.sub(r'<[^>]+>', '', text).strip()

        return text if len(text) > 100 else None
    except:
        return None

# ============================================================================
# 계정명 매칭 함수
# ============================================================================

def find_account_value(data, keywords):
    """계정값 유연하게 찾기"""
    try:
        if isinstance(data, pd.DataFrame):
            for keyword in keywords:
                for col in ['account_name', 'account_nm', 'acc_name']:
                    if col in data.columns:
                        match = data[data[col].astype(str).str.contains(keyword, na=False, case=False)]
                        if not match.empty:
                            for val_col in ['fs_amount', 'amount', 'thstrm_amount']:
                                if val_col in match.columns:
                                    val = match.iloc[0][val_col]
                                    if pd.notna(val):
                                        return float(val)
        elif isinstance(data, dict):
            for keyword in keywords:
                for key, value in data.items():
                    if isinstance(key, str) and keyword.lower() in key.lower():
                        return float(value) if value else None
    except:
        pass

    return None

# ============================================================================
# Node 1: 정량 재무 분석 엔진
# ============================================================================

def financial_rule_engine(financial_df, analysis_dict=None) -> dict:
    """전문가 수준의 정량 분석"""

    risk_scores = {
        "revenue_quality": 0,
        "liquidity_stress": 0,
        "leverage_risk": 0,
    }

    detailed_analysis = {}

    # 매출 질 평가
    try:
        if financial_df is not None:
            sales = find_account_value(financial_df, ['매출액', '매출', 'revenue'])
            ar = find_account_value(financial_df, ['매출채권', '기타채권'])
            ocf = find_account_value(financial_df, ['영업활동', '영업현금'])

            revenue_quality_score = 20

            if sales and ar:
                ar_turnover = sales / ar if ar > 0 else 0

                if ar_turnover < 2:
                    revenue_quality_score = 70
                    detailed_analysis["ar_warning"] = f"⚠️ 매출채권 회전율 저위: {ar_turnover:.2f}배"
                elif ar_turnover < 4:
                    revenue_quality_score = 50
                    detailed_analysis["ar_caution"] = f"⚠️ 매출채권 회전율 주의: {ar_turnover:.2f}배"
                else:
                    detailed_analysis["ar_quality"] = f"✅ 매출채권 회전율 양호: {ar_turnover:.2f}배"

            if ocf is not None:
                if ocf < 0:
                    revenue_quality_score = max(revenue_quality_score, 85)
                    detailed_analysis["ocf_warning"] = f"🚨 영업현금흐름 음수: {ocf:,.0f}원"
                else:
                    detailed_analysis["ocf_quality"] = f"✅ 영업현금흐름 양수: {ocf:,.0f}원"

            risk_scores["revenue_quality"] = revenue_quality_score
    except:
        risk_scores["revenue_quality"] = 40

    # 유동성 및 부채 평가
    try:
        if financial_df is not None:
            current_assets = find_account_value(financial_df, ['유동자산'])
            current_liabilities = find_account_value(financial_df, ['유동부채'])
            total_assets = find_account_value(financial_df, ['자산총계'])
            total_debt = find_account_value(financial_df, ['부채총계'])

            liquidity_score = 20

            if current_assets is not None and current_liabilities is not None and current_liabilities > 0:
                current_ratio = (current_assets / current_liabilities) * 100

                if current_ratio < 100:
                    liquidity_score = 90
                    detailed_analysis["liquidity_risk"] = f"🚨 단기유동성 압박: {current_ratio:.1f}%"
                elif current_ratio < 150:
                    liquidity_score = 60
                    detailed_analysis["liquidity_caution"] = f"⚠️ 유동성 주의: {current_ratio:.1f}%"
                else:
                    detailed_analysis["liquidity_healthy"] = f"✅ 유동성 양호: {current_ratio:.1f}%"

            risk_scores["liquidity_stress"] = liquidity_score

            leverage_score = 20

            if total_assets is not None and total_debt is not None:
                equity = total_assets - total_debt
                if equity > 0:
                    debt_ratio = (total_debt / equity) * 100

                    if debt_ratio > 200:
                        leverage_score = 80
                        detailed_analysis["leverage_high"] = f"🚨 부채비율 상승: {debt_ratio:.1f}%"
                    elif debt_ratio > 160:
                        leverage_score = 50
                        detailed_analysis["leverage_caution"] = f"⚠️ 부채비율 주의: {debt_ratio:.1f}%"
                    else:
                        detailed_analysis["leverage_healthy"] = f"✅ 부채비율 정상: {debt_ratio:.1f}%"

            risk_scores["leverage_risk"] = leverage_score
    except:
        risk_scores["liquidity_stress"] = 40
        risk_scores["leverage_risk"] = 40

    # 종합 점수
    financial_risk_score = (
        risk_scores["revenue_quality"] * 0.40 +
        risk_scores["liquidity_stress"] * 0.35 +
        risk_scores["leverage_risk"] * 0.25
    )

    return {
        "financial_risk_score": round(financial_risk_score, 1),
        "risk_level": "고위험" if financial_risk_score >= 70 else "정상",
        "component_scores": risk_scores,
        "detailed_findings": detailed_analysis
    }

# ============================================================================
# Node 2: 경영진 소명 및 전략적 리포트
# ============================================================================

def management_explanations(corp_name: str, analysis: dict, notes: str, llm) -> str:
    """경영진 관점의 소명"""

    prompt = f"""당신은 {corp_name}의 경영진 대변인으로, 재무 투명성 및 전략적 의사결정을 설명합니다.

【정량 분석 결과】
- 종합 위험도: {analysis.get('financial_risk_score', 'N/A')}/100
- 위험 수준: {analysis.get('risk_level', 'N/A')}
- 세부 지표: {str(analysis.get('component_scores', {}))}

【재무제표 주석 발췌】
{notes[:2000] if notes else "주석 없음"}

【소명 내용】
국제회계기준(K-IFRS)에 따른 당사의 재무 보고를 설명드립니다.

1. **재무 건전성 입증**
   - 정량 분석 결과의 세부 지표를 근거로 당사의 체계적 재무관리를 소명하십시오.
   - 부채비율, 유동비율, 현금흐름 관련 객관적 지표를 명시하십시오.

2. **전략적 자산 취득의 정당화**
   - 주석에서 언급된 무형자산, 종속기업 투자, 플랫폼 사업을 '미래 성장 동력'으로 정당화하십시오.
   - K-IFRS 회계기준에 따른 보수적 처리 현황을 강조하십시오.

3. **리스크 관리 현황**
   - 당사의 선제적 리스크 관리 체계를 설명하십시오.
   - 회계 투명성 및 기업지배구조 개선 현황을 소명하십시오.

【최종 목표】
법정 진술인처럼 객관적이고 신뢰할 수 있는 재무 보고를 수행하되,
K-IFRS 기준 및 주석의 구체적 근거를 인용하여 소명하십시오.
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except:
        return "재무 소명 생성 중 오류가 발생했습니다."

# ============================================================================
# Node 3: 잠재 리스크 지적 (감시 관점)
# ============================================================================

def stakeholder_caveats(corp_name: str, mgmt_response: str, notes: str, analysis: dict, llm) -> str:
    """이해관계자 및 감시인 관점의 리스크 지적"""

    prompt = f"""당신은 기업지배구조 및 회계감시 전문가로, 국제 투자자펀드의 의뢰로 {corp_name}의 재무 투명성을 감시합니다.

【정량 분석 결과】
- 종합 위험도: {analysis.get('financial_risk_score', 'N/A')}/100
- 위험 수준: {analysis.get('risk_level', 'N/A')}

【경영진의 소명】
{mgmt_response[:1500]}

【재무제표 주석 전문】
{notes if notes else "주석 없음"}

【감시 및 검증】

겉보기 재무 건전성에도 불구하고, 주석에 대한 정밀 분석을 수행합니다.

**🚨 ① 우발채무 및 계류 중인 소송 사건 (Contingent Liabilities)**
   - 주석에서 진행 중인 소송, 분쟁, 법적 리스크를 추적하십시오.
   - 미결제 우발채무 규모와 해결 시점의 불확실성을 지적하십시오.
   - 발견 내용: "주석 [◯절. ~]에 명시된 ~건의 소송은..."으로 구체 인용하십시오.

**🤝 ② 특수관계자 간 거래 및 자금 대여 내역 (Related Party Transactions)**
   - 주석에서 지배주주, 경영진, 계열사 간의 자금 이동을 추적하십시오.
   - 부당한 거래 가격 책정, 담보 제공, 보증 약정의 투명성을 지적하십시오.
   - 발견 내용: "주석 [◯절. 특수관계자 거래]에 따르면 ~..."으로 구체 인용하십시오.

**📉 ③ 종속·관계기업 자산손상차손 및 투자 손실 (Asset Impairment)**
   - 주석에서 M&A 자산, 무형자산, 투자 관련 손상차손을 추적하십시오.
   - 과거 인수 기업의 영업 부진, 손상 인식 규모와 진정성을 의문 제기하십시오.
   - 발견 내용: "주석 [◯절. 자산손상차손]에 따르면 ~..."으로 구체 인용하십시오.

【최종 결론】
투자자 관점에서:
- 제시된 위험 요소가 얼마나 심각한가?
- 추가 공시 또는 감시가 필요한가?
- 투자 진행 여부에 대한 권고를 제시하십시오. (강력 권고 / 조건부 권고 / 주의 / 권고 유보)
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except:
        return "리스크 검증 생성 중 오류가 발생했습니다."

# ============================================================================
# 분석 결과 파싱 및 정리 함수
# ============================================================================

def extract_risk_categories(caveats_text: str) -> dict:
    """Node 3 출력에서 리스크 카테고리별로 핵심 내용 추출"""
    categories = {
        "contingent_liabilities": [],
        "related_party_transactions": [],
        "asset_impairment": [],
        "investment_assessment": ""
    }

    # 우발채무 섹션 추출 (더 유연한 패턴)
    contingent_patterns = [
        r'[①1][\.\s]*우발채무.*?(?=[②2]|③3|【|$)',
        r'우발채무.*?(?=특수관계자|자산손상|【|$)',
    ]
    contingent_text = ""
    for pattern in contingent_patterns:
        match = re.search(pattern, caveats_text, re.DOTALL | re.IGNORECASE)
        if match:
            contingent_text = match.group(0)
            break

    if contingent_text:
        # 주석에서 언급된 구체적인 항목 찾기
        lines = contingent_text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['소송', '건', '억', '만', '우발', '주석', '분쟁', '법적']):
                cleaned = line.strip().replace('- ', '').replace('• ', '').strip()
                if cleaned and len(cleaned) > 5:
                    categories["contingent_liabilities"].append(cleaned)

    # 특수관계자 거래 섹션 추출
    related_patterns = [
        r'[②2][\.\s]*특수관계자.*?(?=[③3]|【|$)',
        r'특수관계자.*?(?=자산손상|【|$)',
    ]
    related_text = ""
    for pattern in related_patterns:
        match = re.search(pattern, caveats_text, re.DOTALL | re.IGNORECASE)
        if match:
            related_text = match.group(0)
            break

    if related_text:
        lines = related_text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['거래', '자금', '대여', '보증', '담보', '지배', '계열사', '관계기업']):
                cleaned = line.strip().replace('- ', '').replace('• ', '').strip()
                if cleaned and len(cleaned) > 5:
                    categories["related_party_transactions"].append(cleaned)

    # 자산손상차손 섹션 추출
    impair_patterns = [
        r'[③3][\.\s]*자산손상.*?(?=【|$)',
        r'종속.*?기업.*?(?=【|$)',
        r'자산손상.*?(?=【|투자.*?권고|$)',
    ]
    impair_text = ""
    for pattern in impair_patterns:
        match = re.search(pattern, caveats_text, re.DOTALL | re.IGNORECASE)
        if match:
            impair_text = match.group(0)
            break

    if impair_text:
        lines = impair_text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['손상', '인수', 'M&A', '투자', '무형자산', '영업부진', '손실']):
                cleaned = line.strip().replace('- ', '').replace('• ', '').strip()
                if cleaned and len(cleaned) > 5:
                    categories["asset_impairment"].append(cleaned)

    # 최종 투자 권고 추출
    final_patterns = [
        r'【최종[\s\S]*?(?:강력|조건부|주의|권고)[\s\S]{0,200}',
        r'투자.*?권고[\s\S]{0,300}',
        r'【최종\s*결론】[\s\S]{0,500}',
    ]
    for pattern in final_patterns:
        match = re.search(pattern, caveats_text, re.IGNORECASE)
        if match:
            categories["investment_assessment"] = match.group(0)
            break

    # 카테고리별로 중복 제거 및 길이 제한
    for key in ["contingent_liabilities", "related_party_transactions", "asset_impairment"]:
        categories[key] = list(dict.fromkeys(categories[key]))[:5]  # 중복 제거, 상위 5개만

    return categories


# ============================================================================
# Streamlit UI
# ============================================================================

# 히어로 배너
st.html("""
<div class="hero-banner">
    <h1>🎯 AI 기반 기업 정량·정성 복합 리스크 검증 시스템</h1>
    <p>Stakeholder-Perspective Enterprise Risk Detection Platform</p>
</div>
""")

# 사이드바: 데이터 수집 설정
with st.sidebar:
    st.markdown("### ⚙️ 데이터 수집 설정")
    st.markdown("---")
    company_name = st.text_input("기업명 입력", value="하이브", key="company_input", placeholder="분석할 기업명을 입력하세요")

    if st.button("🔍 데이터 수집 시작", key="fetch_data", use_container_width=True):
        st.session_state.fetch_triggered = True

    st.markdown("---")
    st.caption("💡 **팁:** 상장사 기업명으로 검색하면 가장 최신의 공시 정보가 조회됩니다.")

# 메인: 데이터 수집 및 분석
if st.session_state.get("fetch_triggered", False):
    # 1. 기업 검색
    with st.spinner("기업 정보 조회 중..."):
        corp_code, corp_name_result = search_company(dart, company_name)

        if not corp_code:
            st.error(f"❌ '{company_name}'을(를) 찾을 수 없습니다.")
            st.stop()

        st.success(f"✅ 기업 발견: {corp_name_result} (코드: {corp_code})")

    # 2. 정기 공시 조회
    with st.spinner("정기 공시 조회 중..."):
        report, report_type = get_periodic_report(dart, corp_code, corp_name_result)

        if report is None:
            st.error("❌ 정기 공시를 찾을 수 없습니다.")
            st.stop()

        rcept_no = report['rcept_no']
        rcept_dt = report['rcept_dt']

        st.success(f"✅ {report_type} 발견 (접수: {rcept_dt})")

    # 3. 재무제표 추출
    with st.spinner("재무제표 추출 중..."):
        financial_df = extract_financial_statement(dart, corp_code)

        if financial_df is None or financial_df.empty:
            st.warning("⚠️ 재무제표 데이터를 찾을 수 없습니다.")
            financial_df = None

    # 4. 주석 추출
    with st.spinner("주석 텍스트 추출 중..."):
        notes = extract_notes(dart, rcept_no)

        if notes:
            st.success(f"✅ 주석 추출 완료 ({len(notes):,}자)")
        else:
            st.warning("⚠️ 주석을 추출하지 못했습니다.")
            notes = "(주석 없음)"

    st.markdown("---")

    # ========================================================================
    # 분석 결과 표시 - 탭 구조
    # ========================================================================

    analysis = financial_rule_engine(financial_df)

    with st.spinner("경영진 소명 생성 중..."):
        mgmt_response = management_explanations(corp_name_result, analysis, notes, llm)

    with st.spinner("리스크 검증 분석 중..."):
        caveats = stakeholder_caveats(corp_name_result, mgmt_response, notes, analysis, llm)

    risk_categories = extract_risk_categories(caveats)

    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📊 정량 리스크 분석", "⚖️ 청문 공방 세션", "🔍 심층 주석 추적"])

    # ========================================================================
    # Tab 1: 정량 리스크 분석
    # ========================================================================
    with tab1:
        st.markdown('<div class="section-header">📈 정량 규칙 엔진 기반의 회계 리스크 점수 산출</div>', unsafe_allow_html=True)

        # 메트릭 카드 (4열)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            risk_score = analysis['financial_risk_score']
            risk_emoji = "🔴" if risk_score >= 70 else "🟡" if risk_score >= 50 else "🟢"
            st.metric(
                "종합 위험도",
                f"{risk_score}/100",
                delta=analysis['risk_level'],
                delta_color="inverse",
                help="높을수록 리스크가 높음"
            )

        with col2:
            st.metric(
                "매출 질 점수",
                f"{analysis['component_scores']['revenue_quality']}/100",
                help="매출채권 회전율, 영업현금흐름 등"
            )

        with col3:
            st.metric(
                "유동성 점수",
                f"{analysis['component_scores']['liquidity_stress']}/100",
                help="단기유동성 압박도 평가"
            )

        with col4:
            st.metric(
                "부채 점수",
                f"{analysis['component_scores']['leverage_risk']}/100",
                help="부채비율 및 자본 구조"
            )

        st.markdown("")

        # 상세 분석 결과 박스
        with st.container(border=True):
            st.markdown('<div class="section-header">📋 분석 상세 결과</div>', unsafe_allow_html=True)

            if analysis['detailed_findings']:
                for key, value in analysis['detailed_findings'].items():
                    st.markdown(f"• {value}")
            else:
                st.markdown("*상세 분석 데이터 없음*")

        st.markdown("")
        st.markdown("---")

        # 최종 요약
        st.markdown('<div class="section-header">📌 기업 기본 정보 & 리스크 평가 종합</div>', unsafe_allow_html=True)

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:
            with st.container(border=True):
                st.markdown("**📊 기업 기본 정보**")
                st.markdown(f"""
                • **기업명:** {corp_name_result}
                • **기업 코드:** {corp_code}
                • **보고서:** {report_type}
                • **공시 접수일:** {rcept_dt}
                """)

        with summary_col2:
            with st.container(border=True):
                st.markdown("**📈 리스크 평가 종합**")
                risk_color = "🔴" if analysis['financial_risk_score'] >= 70 else "🟡" if analysis['financial_risk_score'] >= 50 else "🟢"
                st.markdown(f"""
                • **종합 위험도:** {risk_color} **{analysis['financial_risk_score']}/100** ({analysis['risk_level']})
                • **매출 질:** {analysis['component_scores']['revenue_quality']}/100
                • **유동성:** {analysis['component_scores']['liquidity_stress']}/100
                • **부채:** {analysis['component_scores']['leverage_risk']}/100
                """)

    # ========================================================================
    # Tab 2: 청문 공방 세션 (경영진 vs 감시자)
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-header">💼 ⚖️ 경영진의 입장 vs 감시자의 관점</div>', unsafe_allow_html=True)
        st.markdown("**K-IFRS 기준의 재무 건전성 입증 vs 기업지배구조·잠재 리스크 검증**")

        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True):
                st.markdown("### 👨‍💼 경영진 소명")
                st.markdown("*Management Response*")
                st.markdown(mgmt_response)

        with col_right:
            with st.container(border=True):
                st.markdown("### ⚠️ 감시자의 리스크 지적")
                st.markdown("*Stakeholder Caveats*")
                st.markdown(caveats)

    # ========================================================================
    # Tab 3: 심층 주석 추적 (리스크 아코디언)
    # ========================================================================
    with tab3:
        st.markdown('<div class="section-header">🔍 주석 기반 리스크 세부 항목 분석</div>', unsafe_allow_html=True)
        st.markdown("**재무제표 주석에서 도출된 잠재 리스크 요소의 상세 검토**")

        st.markdown("")

        # 우발채무 아코디언
        with st.expander("🚨 우발채무 및 계류 중인 소송", expanded=False):
            if risk_categories["contingent_liabilities"]:
                for item in risk_categories["contingent_liabilities"]:
                    st.markdown(f"• {item}")
            else:
                st.markdown("""
                본 분석에서 보고서 주석 섹션을 검토하여 다음을 추적합니다:
                - 진행 중인 소송 및 분쟁 사건
                - 미결제 우발채무 규모 및 시기
                - 법적 리스크의 불확실성
                """)

        # 특수관계자 거래 아코디언
        with st.expander("🤝 특수관계자 간 거래 및 자금 이동", expanded=False):
            if risk_categories["related_party_transactions"]:
                for item in risk_categories["related_party_transactions"]:
                    st.markdown(f"• {item}")
            else:
                st.markdown("""
                본 분석에서 주석에서 추적하는 사항:
                - 지배주주·경영진·계열사 간 자금 이동
                - 부당한 거래 가격 책정의 가능성
                - 담보·보증 약정의 투명성
                """)

        # 자산손상차손 아코디언
        with st.expander("📉 종속·관계기업 자산손상 및 투자 손실", expanded=False):
            if risk_categories["asset_impairment"]:
                for item in risk_categories["asset_impairment"]:
                    st.markdown(f"• {item}")
            else:
                st.markdown("""
                본 분석에서 검토하는 사항:
                - M&A 및 인수 자산의 부진 현황
                - 무형자산 및 투자 손상 규모
                - 손상 인식의 적절성 평가
                """)

        # 투자 권고 아코디언
        with st.expander("💼 투자 권고 및 최종 결론", expanded=True):
            if risk_categories["investment_assessment"]:
                st.markdown(risk_categories["investment_assessment"])
            else:
                st.markdown(caveats[-500:])

        st.markdown("---")

        with st.container(border=True):
            st.markdown("""
            ### 💡 시스템 사용 주의사항

            본 분석은 공개 정보 기반의 **정성적 검증 시스템**으로, 투자 의사결정의 **보조 자료**로만 활용되어야 합니다.

            - **정량 분석:** 재무제표의 객관적 지표를 기반한 위험 점수
            - **경영진 소명:** 기업이 공시한 내용의 해석 및 재무 논리의 일관성 검증
            - **리스크 지적:** 주석 및 공시 정보에서 발견된 잠재적 위험 요소의 추적

            **최종 투자 의사결정은 반드시 전문가의 자문을 거쳐야 합니다.**
            """)

else:
    # 초기 화면
    with st.container(border=True):
        st.markdown("""
        ### 📊 시스템에 오신 것을 환영합니다

        좌측 사이드바에서 기업명을 입력하고 **'데이터 수집 시작'** 버튼을 클릭하세요.
        """)

    st.markdown("---")

    st.subheader("🎯 시스템 개요")
    st.markdown("""
    본 시스템은 **정량 분석 → 경영진 소명 → 이해관계자 검증**의 3단계 프로세스를 통해
    기업의 재무 투명성과 잠재 리스크를 종합적으로 분석합니다.

    ### 📊 분석 단계 상세 설명

    **1️⃣ 정량 재무 분석 (Quantitative Analysis)**
    - 회계 규칙 엔진 기반의 객관적 위험 점수 산출
    - 매출 질, 유동성, 부채 수준에 대한 정량적 평가
    - 매출채권 회전율, 유동비율, 부채비율 등 핵심 지표 분석

    **2️⃣ 경영진 소명 (Management Explanations)**
    - K-IFRS 기준에 따른 재무 상황 설명
    - 전략적 자산 취득 및 투자 정당화
    - 기업의 재무 보고의 논리와 일관성 검증

    **3️⃣ 이해관계자 검증 (Auditor & Stakeholder Caveats)**
    - 🚨 **우발채무 및 계류 중인 소송:** 미결제 법적 리스크 추적
    - 🤝 **특수관계자 거래:** 부당 거래 및 자금 이동 검증
    - 📉 **자산손상차손:** M&A 및 투자 손실 현황 분석

    ### 🔐 데이터 출처
    - **DART (Data Analysis, Retrieval and Transfer):** 한국 상장회사의 공시 정보
    - **Claude LLM:** 정성적 분석 및 리스크 검증
    - **Financial Rule Engine:** 전문가 수준의 재무 지표 분석
    """)

    st.markdown("---")
    st.caption("© 2026 이해관계자 관점 기업 리스크 탐지 시스템 | 학회 발표용 전문 분석 플랫폼")
