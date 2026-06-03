# -*- coding: utf-8 -*-
"""
기업 정량·정성 복합 리스크 검증 시스템 - 웹 인터페이스
(Enterprise Risk Detection System - Web Interface)

전문 금융·회계 분석 플랫폼
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

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(".env")

# ============================================================================
# Streamlit 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="Enterprise Risk Detection System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    input {
        font-size: 1.5em !important;
        letter-spacing: 0.5px !important;
    }

    button {
        font-size: 1.5em !important;
        font-weight: 600 !important;
    }

    body {
        background: linear-gradient(135deg, #f0f7f2 0%, #e8f5e9 100%);
        color: #1b3a2a;
    }

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

    [data-testid="stSidebar"] {
        background: white !important;
        backdrop-filter: none !important;
        border-right: 1px solid #e0e0e0;
    }

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

    .section-header {
        border-left: 4px solid #1b4332;
        padding-left: 16px;
        margin: 24px 0 16px 0;
        font-weight: 600;
        color: #1b4332;
        font-size: 1.1em;
    }

    .metric-card {
        background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2);
    }

    [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
        border-radius: 16px;
    }

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

    [data-testid="stExpander"] {
        border: 1px solid #a5d6a7 !important;
        border-radius: 12px !important;
        background: rgba(232, 245, 233, 0.3) !important;
        padding: 16px !important;
    }

    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        font-size: 1.05em !important;
        line-height: 1.8 !important;
        padding: 12px 0 !important;
        word-break: break-word !important;
    }

    [data-testid="stExpander"] p {
        margin: 12px 0 !important;
        line-height: 1.8 !important;
        font-size: 1.01em !important;
    }

    [data-testid="stExpander"] ul {
        margin: 12px 0 !important;
        padding-left: 24px !important;
    }

    [data-testid="stExpander"] li {
        margin: 8px 0 !important;
        line-height: 1.8 !important;
        font-size: 1.01em !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
        font-size: 1.5em !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
    }

    .stTextInput > div > div > input {
        background-color: white !important;
        color: black !important;
        border: 1px solid #d0d0d0 !important;
        padding: 18px 16px !important;
        height: 70px !important;
        box-sizing: border-box !important;
        line-height: 1.4 !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: transparent !important;
    }

    .stTextInput label {
        font-size: 1.15em !important;
        color: #1b4332 !important;
        margin-bottom: 8px !important;
    }

    .stSuccess {
        display: none;
    }

    .stWarning {
        display: none;
    }

    .stError {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #c41c3b;
    }

    .stInfo {
        background: rgba(45, 106, 79, 0.05);
        border-left: 4px solid #40916c;
    }

    a {
        color: #2d6a4f !important;
        text-decoration: none;
        font-weight: 500;
    }

    a:hover {
        color: #1b4332 !important;
        text-decoration: underline;
    }

    .conclusion-box {
        background: linear-gradient(135deg, rgba(27, 67, 50, 0.08) 0%, rgba(45, 106, 79, 0.06) 100%);
        border-left: 5px solid #1b4332;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        font-weight: 500;
    }

    h3 {
        font-size: 1.25em;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    h4 {
        font-size: 1.1em;
        margin-top: 15px;
        margin-bottom: 8px;
    }

    .hero-gradient {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 700px;
        height: 700px;
        background: radial-gradient(circle, rgba(45, 106, 79, 0.08) 0%, rgba(45, 106, 79, 0.04) 50%, transparent 75%);
        border-radius: 50%;
        filter: blur(100px);
        z-index: 0;
        pointer-events: none;
    }

    .input-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        gap: 40px;
        position: relative;
        z-index: 1;
    }

    .input-section h1 {
        font-size: 3.5em;
        font-weight: 700;
        color: #1b4332;
        margin: 0;
        text-align: center;
        letter-spacing: -1px;
    }

    .input-section p {
        font-size: 1.35em;
        color: #558b63;
        text-align: center;
        margin: 0;
        max-width: 1000px;
        font-weight: 500;
        white-space: normal;
        word-wrap: break-word;
    }

    .input-container {
        display: flex;
        gap: 12px;
        width: 100%;
        max-width: 600px;
    }

    [data-testid="stTextInput"] {
        flex: 1;
    }

    [data-testid="stButton"] button {
        height: 70px !important;
        line-height: 1.4 !important;
        padding: 18px 24px !important;
        box-sizing: border-box !important;
    }

    .disclaimer {
        font-size: 0.95em;
        color: #a8a8a8;
        text-align: center;
        margin-top: 30px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

st.html("""
<div class="deco-blob-1"></div>
<div class="deco-blob-2"></div>
<div class="hero-gradient"></div>
""")

# ============================================================================
# 초기화
# ============================================================================

@st.cache_resource
def init_dart_api():
    dart_api_key = os.getenv("DART_API_KEY")
    if not dart_api_key:
        st.error("DART_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
        st.stop()

    try:
        dart = OpenDartReader(dart_api_key)
        return dart
    except Exception as e:
        st.error(f"DART API 초기화 실패: {e}")
        st.stop()

@st.cache_resource
def init_llm():
    api_key = os.getenv("Anthropic_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
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
    risk_scores = {
        "revenue_quality": 0,
        "liquidity_stress": 0,
        "leverage_risk": 0,
    }

    detailed_analysis = {}

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
                    detailed_analysis["ar_warning"] = f"매출채권 회전율 저위: {ar_turnover:.2f}배"
                elif ar_turnover < 4:
                    revenue_quality_score = 50
                    detailed_analysis["ar_caution"] = f"매출채권 회전율 주의: {ar_turnover:.2f}배"
                else:
                    detailed_analysis["ar_quality"] = f"매출채권 회전율 양호: {ar_turnover:.2f}배"

            if ocf is not None:
                if ocf < 0:
                    revenue_quality_score = max(revenue_quality_score, 85)
                    detailed_analysis["ocf_warning"] = f"영업현금흐름 음수: {ocf:,.0f}원"
                else:
                    detailed_analysis["ocf_quality"] = f"영업현금흐름 양수: {ocf:,.0f}원"

            risk_scores["revenue_quality"] = revenue_quality_score
    except:
        risk_scores["revenue_quality"] = 40

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
                    detailed_analysis["liquidity_risk"] = f"단기유동성 압박: {current_ratio:.1f}%"
                elif current_ratio < 150:
                    liquidity_score = 60
                    detailed_analysis["liquidity_caution"] = f"유동성 주의: {current_ratio:.1f}%"
                else:
                    detailed_analysis["liquidity_healthy"] = f"유동성 양호: {current_ratio:.1f}%"

            risk_scores["liquidity_stress"] = liquidity_score

            leverage_score = 20

            if total_assets is not None and total_debt is not None:
                equity = total_assets - total_debt
                if equity > 0:
                    debt_ratio = (total_debt / equity) * 100

                    if debt_ratio > 200:
                        leverage_score = 80
                        detailed_analysis["leverage_high"] = f"부채비율 상승: {debt_ratio:.1f}%"
                    elif debt_ratio > 160:
                        leverage_score = 50
                        detailed_analysis["leverage_caution"] = f"부채비율 주의: {debt_ratio:.1f}%"
                    else:
                        detailed_analysis["leverage_healthy"] = f"부채비율 정상: {debt_ratio:.1f}%"

            risk_scores["leverage_risk"] = leverage_score
    except:
        risk_scores["liquidity_stress"] = 40
        risk_scores["leverage_risk"] = 40

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
# Node 2: 경영진 설명
# ============================================================================

def management_explanations(corp_name: str, analysis: dict, notes: str, llm) -> str:
    prompt = f"""당신은 {corp_name}의 경영진 대변인으로, 재무 투명성 및 전략적 의사결정을 설명합니다.

【정량 분석 결과】
- 종합 위험도: {analysis.get('financial_risk_score', 'N/A')}/100
- 위험 수준: {analysis.get('risk_level', 'N/A')}
- 세부 지표: {str(analysis.get('component_scores', {}))}

【재무제표 주석 발췌】
{notes[:2000] if notes else "주석 없음"}

【설명 내용】
국제회계기준(K-IFRS)에 따른 당사의 재무 보고를 설명드립니다.

1. **재무 건전성 입증**
   - 정량 분석 결과의 세부 지표를 근거로 당사의 체계적 재무관리를 설명하십시오.
   - 부채비율, 유동비율, 현금흐름 관련 객관적 지표를 명시하십시오.

2. **전략적 자산 취득의 정당화**
   - 주석에서 언급된 무형자산, 종속기업 투자, 사업을 미래 성장 동력으로 설명하십시오.
   - K-IFRS 회계기준에 따른 보수적 처리 현황을 강조하십시오.

3. **리스크 관리 현황**
   - 당사의 선제적 리스크 관리 체계를 설명하십시오.
   - 회계 투명성 및 기업지배구조 개선 현황을 소명하십시오.
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except:
        return "재무 설명 생성 중 오류가 발생했습니다."

# ============================================================================
# Node 3: 정성적 크로스체킹
# ============================================================================

def stakeholder_caveats(corp_name: str, mgmt_response: str, notes: str, analysis: dict, llm) -> str:
    prompt = f"""당신은 기업지배구조 및 회계감시 전문가로, 국제 투자자의 의뢰로 {corp_name}의 재무 투명성을 검증합니다.

【정량 분석 결과】
- 종합 위험도: {analysis.get('financial_risk_score', 'N/A')}/100
- 위험 수준: {analysis.get('risk_level', 'N/A')}

【경영진의 설명】
{mgmt_response[:1500]}

【재무제표 주석】
{notes if notes else "주석 없음"}

【정성적 검증】

재무 건전성에도 불구하고, 주석에 대한 정밀 분석을 수행합니다.

**① 우발채무 및 계류 중인 소송**
   - 주석에서 진행 중인 소송, 분쟁, 법적 리스크를 추적하십시오.
   - 미결제 우발채무 규모와 해결 시점의 불확실성을 지적하십시오.
   - 발견 내용: 구체적으로 인용하십시오.

**② 특수관계자 거래 및 자금 이동**
   - 주석에서 지배주주, 경영진, 계열사 간의 자금 이동을 추적하십시오.
   - 부당한 거래 가격 책정, 담보 제공, 보증 약정의 투명성을 지적하십시오.
   - 발견 내용: 구체적으로 인용하십시오.

**③ 자산손상차손 및 투자 손실**
   - 주석에서 M&A 자산, 무형자산, 투자 관련 손상을 추적하십시오.
   - 과거 인수 기업의 영업 부진, 손상 인식 규모를 분석하십시오.
   - 발견 내용: 구체적으로 인용하십시오.

【최종 평가】
투자자 관점에서:
- 제시된 위험 요소가 얼마나 심각한가?
- 추가 공시 또는 감시가 필요한가?
- 투자 진행 여부에 대한 평가를 명시하십시오.
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except:
        return "정성적 검증 생성 중 오류가 발생했습니다."

# ============================================================================
# 리스크 카테고리 추출
# ============================================================================

def extract_risk_categories(caveats_text: str) -> dict:
    categories = {
        "contingent_liabilities": [],
        "related_party_transactions": [],
        "asset_impairment": [],
        "investment_assessment": ""
    }

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
        lines = contingent_text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['소송', '건', '억', '만', '우발', '주석', '분쟁', '법적']):
                cleaned = line.strip().replace('- ', '').replace('• ', '').strip()
                if cleaned and len(cleaned) > 5:
                    categories["contingent_liabilities"].append(cleaned)

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

    for key in ["contingent_liabilities", "related_party_transactions", "asset_impairment"]:
        categories[key] = list(dict.fromkeys(categories[key]))[:5]

    return categories

# ============================================================================
# UI - 사이드바 공통
# ============================================================================

with st.sidebar:
    st.markdown("### 분석 설정")
    st.markdown("")
    st.markdown("**DART API 키 연동**")

# ============================================================================
# UI - 초기 화면 vs 분석 결과
# ============================================================================

# ============================================================================
# UI - 초기 화면 로직
# ============================================================================

if not st.session_state.get("fetch_triggered", False):
    st.html('<div class="hero-gradient"></div>')

    col_center = st.columns([1])[0]

    with col_center:
        st.markdown("""
        <div class="input-section">
            <h1>기업 리스크 검증</h1>
            <p>재무제표 정량 분석과 주석 정성 검증으로 기업의 투명성과 잠재 리스크를 종합 평가합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        col_input, col_btn = st.columns([0.7, 0.3], gap="small")

        with col_input:
            company_name = st.text_input(
                "기업명",
                value="",
                key="company_input",
                placeholder="",
                label_visibility="collapsed"
            )

        with col_btn:
            if st.button("분석", key="fetch_data", use_container_width=True):
                if company_name.strip():
                    st.session_state.company_name = company_name
                    st.session_state.fetch_triggered = True
                    st.rerun()
                else:
                    st.error("기업명을 입력하세요")

        st.markdown('<p class="disclaimer">본 분석은 공개 정보 기반의 정량 및 정성적 검증 시스템으로, 투자 의사결정의 보조 자료로만 활용하는 것을 권장드립니다.</p>', unsafe_allow_html=True)

# ============================================================================
# UI - 분석 결과
# ============================================================================

elif st.session_state.get("fetch_triggered", False):
    company_name = st.session_state.get("company_name", "")

    with st.spinner("데이터 수집 중..."):
        corp_code, corp_name_result = search_company(dart, company_name)

        if not corp_code:
            st.error(f"'{company_name}'을(를) 찾을 수 없습니다.")
            st.stop()

    with st.spinner("공시 정보 조회 중..."):
        report, report_type = get_periodic_report(dart, corp_code, corp_name_result)

        if report is None:
            st.error("정기 공시를 찾을 수 없습니다.")
            st.stop()

        rcept_no = report['rcept_no']
        rcept_dt = report['rcept_dt']

    with st.spinner("재무 데이터 추출 중..."):
        financial_df = extract_financial_statement(dart, corp_code)

        if financial_df is None or financial_df.empty:
            st.warning("재무제표 데이터를 찾을 수 없습니다.")
            financial_df = None

    with st.spinner("주석 추출 중..."):
        notes = extract_notes(dart, rcept_no)

        if not notes:
            notes = "(주석 없음)"

    st.markdown("---")

    analysis = financial_rule_engine(financial_df)

    with st.spinner("분석 진행 중..."):
        mgmt_response = management_explanations(corp_name_result, analysis, notes, llm)
        caveats = stakeholder_caveats(corp_name_result, mgmt_response, notes, analysis, llm)

    risk_categories = extract_risk_categories(caveats)

    tab1, tab2, tab3 = st.tabs(["정량 재무 분석", "정성적 크로스체킹", "주석 기반 리스크"])

    # ========================================================================
    # Tab 1: 정량 재무 분석
    # ========================================================================
    with tab1:
        st.markdown('<div class="section-header">정량 규칙 엔진 기반 회계 리스크 점수</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("**기업 기본 정보**")
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)

            with info_col1:
                st.metric("기업명", corp_name_result)
            with info_col2:
                st.metric("기업코드", corp_code)
            with info_col3:
                st.metric("보고서", report_type)
            with info_col4:
                st.metric("공시일", rcept_dt)

        st.markdown("")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            risk_score = analysis['financial_risk_score']
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
                help="매출채권 회전율, 영업현금흐름"
            )

        with col3:
            st.metric(
                "유동성 점수",
                f"{analysis['component_scores']['liquidity_stress']}/100",
                help="단기유동성 압박도"
            )

        with col4:
            st.metric(
                "부채 점수",
                f"{analysis['component_scores']['leverage_risk']}/100",
                help="부채비율 및 자본 구조"
            )

        st.markdown("")
        st.markdown("---")

        st.markdown('<div class="section-header">분석 상세 결과</div>', unsafe_allow_html=True)

        with st.container(border=True):
            if analysis['detailed_findings']:
                for key, value in analysis['detailed_findings'].items():
                    st.markdown(f"**{value}**")
            else:
                st.markdown("상세 분석 데이터 없음")

        st.markdown("")
        st.markdown("---")

        st.markdown('<div class="section-header">정량 리스크 평가 총평</div>', unsafe_allow_html=True)

        with st.container(border=True):
            risk_score = analysis['financial_risk_score']

            if risk_score >= 70:
                assessment = "현재 정량 지표상 상당한 재무 리스크가 식별됩니다. 부채비율, 유동성, 현금흐름 등의 주요 지표에서 개선이 필요합니다. 추가적인 정성 분석을 통해 이러한 위험 요소가 기업의 구조적 문제인지, 또는 일시적 변동인지 파악해야 합니다."
            elif risk_score >= 50:
                assessment = "정량 지표상 중간 수준의 리스크가 식별됩니다. 특정 회계 지표에서 주의가 필요하며, 경영진의 대응 방안 및 개선 계획을 검토할 필요가 있습니다. 정성 분석을 통해 경영 안정성을 추가 확인하십시오."
            else:
                assessment = "정량 지표상 위험도는 정상 수준입니다. 다만, 주석 정보와의 종합 검토를 통해 잠재적 리스크가 있는지 추가 확인이 권장됩니다."

            st.markdown(assessment)

    # ========================================================================
    # Tab 2: 정성적 크로스체킹
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-header">K-IFRS 기준 재무 건전성 검증</div>', unsafe_allow_html=True)

        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True):
                st.markdown("### 경영진 설명")
                st.markdown(mgmt_response)

        with col_right:
            with st.container(border=True):
                st.markdown("### 정성적 검증")
                st.markdown(caveats)

    # ========================================================================
    # Tab 3: 주석 기반 리스크
    # ========================================================================
    with tab3:
        st.markdown('<div class="section-header">주석 기반 리스크 세부 분석</div>', unsafe_allow_html=True)

        with st.expander("우발채무 및 계류 중인 소송", expanded=False):
            if risk_categories["contingent_liabilities"]:
                for item in risk_categories["contingent_liabilities"]:
                    st.markdown(f"- {item}")
            else:
                st.markdown("""
본 분석에서 추적하는 항목:
- 진행 중인 소송 및 분쟁 사건
- 미결제 우발채무 규모 및 해결 시점
- 법적 리스크의 불확실성
                """)

        with st.expander("특수관계자 거래 및 자금 이동", expanded=False):
            if risk_categories["related_party_transactions"]:
                for item in risk_categories["related_party_transactions"]:
                    st.markdown(f"- {item}")
            else:
                st.markdown("""
본 분석에서 추적하는 항목:
- 지배주주·경영진·계열사 간 자금 이동
- 부당한 거래 가격 책정의 가능성
- 담보·보증 약정의 투명성
                """)

        with st.expander("자산손상차손 및 투자 손실", expanded=False):
            if risk_categories["asset_impairment"]:
                for item in risk_categories["asset_impairment"]:
                    st.markdown(f"- {item}")
            else:
                st.markdown("""
본 분석에서 추적하는 항목:
- M&A 및 인수 자산의 부진 현황
- 무형자산 및 투자 손상 규모
- 손상 인식의 적절성 평가
                """)

        st.markdown("")
        st.markdown("---")

        st.markdown('<div class="conclusion-box">최종 평가 및 권고</div>', unsafe_allow_html=True)

        with st.container(border=True):
            if risk_categories["investment_assessment"]:
                st.markdown(risk_categories["investment_assessment"])
            else:
                st.markdown("최종 평가를 도출하기 위해 상기 정량 분석과 정성 검증을 종합하여 투자 여부를 판단하십시오.")
