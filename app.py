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
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 사이드바 토글 버튼 완전 제거 */
    button[aria-label="Collapse sidebar"] {
        display: none !important;
    }
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

    /* 사이드바 관련 CSS 제거 - expanded 상태 유지 */

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
    debt_ratio = None
    current_ratio = None

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
        "detailed_findings": detailed_analysis,
        "debt_ratio": round(debt_ratio, 2) if debt_ratio else None,
        "current_ratio": round(current_ratio, 2) if current_ratio else None
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

    if not caveats_text or len(caveats_text) < 50:
        return categories

    contingent_keywords = ['소송', '분쟁', '우발', '법적', '청구', '피소', '소장']
    related_keywords = ['거래', '자금', '대여', '보증', '담보', '지배', '계열사', '관계기업']
    impair_keywords = ['손상', '인수', 'M&A', '투자', '무형자산', '부진', '손실']

    lines = caveats_text.split('\n')

    current_section = None
    for line in lines:
        line_clean = line.strip()

        if not line_clean or len(line_clean) < 5:
            continue

        if any(kw in line_clean for kw in ['우발', '소송', '분쟁']):
            current_section = "contingent_liabilities"
        elif any(kw in line_clean for kw in ['특수', '관계자', '계열사']):
            current_section = "related_party_transactions"
        elif any(kw in line_clean for kw in ['손상', '투자손실', 'M&A']):
            current_section = "asset_impairment"
        elif any(kw in line_clean for kw in ['최종', '권고', '평가']):
            current_section = None

        if current_section:
            is_content_line = (
                (current_section == "contingent_liabilities" and any(kw in line_clean for kw in contingent_keywords)) or
                (current_section == "related_party_transactions" and any(kw in line_clean for kw in related_keywords)) or
                (current_section == "asset_impairment" and any(kw in line_clean for kw in impair_keywords))
            )

            if is_content_line and len(line_clean) > 5:
                cleaned = line_clean.replace('- ', '').replace('• ', '').replace('*', '').strip()
                if cleaned and not cleaned.startswith('['):
                    categories[current_section].append(cleaned)

    if '최종' in caveats_text or '권고' in caveats_text:
        lines_for_final = caveats_text.split('\n')
        for i, line in enumerate(lines_for_final):
            if any(kw in line for kw in ['최종', '권고', '투자']):
                categories["investment_assessment"] = '\n'.join(lines_for_final[i:i+5])[:500]
                break

    for key in ["contingent_liabilities", "related_party_transactions", "asset_impairment"]:
        categories[key] = list(dict.fromkeys(categories[key]))[:5]

    return categories

# ============================================================================
# 정성 위험도 점수 추출
# ============================================================================

def extract_qualitative_risk_score(risk_categories: dict) -> dict:
    """
    Node 3의 stakeholder_caveats() 결과에서 정성 위험도 점수를 계산합니다.

    개선된 계산 기준 (항목 개수 반영):
    - 우발채무 (contingent_liabilities): 항목당 15점 (최대 45점)
    - 특수관계자거래 (related_party_transactions): 항목당 20점 (최대 40점)
    - 자산손상 (asset_impairment): 항목당 20점 (최대 40점)
    - 투자 평가 (investment_assessment): 25점 (있으면 25, 없으면 0)
    - 총 최대 100점 (다양한 점수 생성 가능)

    Args:
        risk_categories: {
            "contingent_liabilities": [...],      # 발견된 우발채무 리스트
            "related_party_transactions": [...],  # 발견된 특수관계자거래 리스트
            "asset_impairment": [...],            # 발견된 자산손상 리스트
            "investment_assessment": ""           # 최종 평가 텍스트
        }

    Returns:
        {
            "qualitative_risk_score": float (0-100),     # 정성 위험도 점수 (다양한 값)
            "risk_count": int,                           # 발견된 리스크 카테고리 개수
            "risk_breakdown": {                          # 카테고리별 발견 항목 개수
                "contingent_liabilities": int,
                "related_party_transactions": int,
                "asset_impairment": int,
                "investment_assessment": int (0 or 1)
            }
        }
    """

    risk_breakdown = {}
    categories_with_risk = 0
    qualitative_risk_score = 0

    # 우발채무 (contingent_liabilities): 항목당 15점 (최대 45점)
    contingent_items = risk_categories.get("contingent_liabilities", [])
    contingent_count = len(contingent_items) if contingent_items else 0
    risk_breakdown["contingent_liabilities"] = contingent_count
    contingent_score = min(contingent_count * 15, 45)
    qualitative_risk_score += contingent_score
    if contingent_count > 0:
        categories_with_risk += 1

    # 특수관계자거래 (related_party_transactions): 항목당 20점 (최대 40점)
    related_items = risk_categories.get("related_party_transactions", [])
    related_count = len(related_items) if related_items else 0
    risk_breakdown["related_party_transactions"] = related_count
    related_score = min(related_count * 20, 40)
    qualitative_risk_score += related_score
    if related_count > 0:
        categories_with_risk += 1

    # 자산손상 (asset_impairment): 항목당 20점 (최대 40점)
    asset_items = risk_categories.get("asset_impairment", [])
    asset_count = len(asset_items) if asset_items else 0
    risk_breakdown["asset_impairment"] = asset_count
    asset_score = min(asset_count * 20, 40)
    qualitative_risk_score += asset_score
    if asset_count > 0:
        categories_with_risk += 1

    # 투자 평가 (investment_assessment): 25점 (텍스트 있으면 추가)
    assessment = risk_categories.get("investment_assessment", "")
    has_assessment = 1 if (assessment and len(assessment.strip()) > 0) else 0
    risk_breakdown["investment_assessment"] = has_assessment
    if has_assessment > 0:
        qualitative_risk_score += 25
        categories_with_risk += 1

    # 최대 100점 제한
    qualitative_risk_score = min(qualitative_risk_score, 100)

    return {
        "qualitative_risk_score": round(qualitative_risk_score, 1),
        "risk_count": categories_with_risk,
        "risk_breakdown": risk_breakdown
    }

# ============================================================================
# Node 4: 가중치 통합 최종 위험 등급
# ============================================================================

def integrate_final_risk_grade(financial_risk_score: float, qualitative_risk_score: float) -> dict:
    """
    정량 위험도(Node 1)와 정성 위험도를 가중치로 통합하여 최종 위험 등급을 산출합니다.

    가중치:
    - 정량(Node 1): 60%
    - 정성: 40%

    최종 점수 = (financial_risk_score × 0.6) + (qualitative_risk_score × 0.4)

    Args:
        financial_risk_score: 정량 위험도 점수 (0-100) from Node 1
        qualitative_risk_score: 정성 위험도 점수 (0-100) from extract_qualitative_risk_score()

    Returns:
        {
            "final_integrated_score": float,           # 최종 통합 점수 (0-100)
            "final_risk_grade": str,                   # "HIGH_RISK" | "MEDIUM_RISK" | "LOW_RISK"
            "color": str,                              # "red" | "orange" | "green"
            "explanation": str                         # 최종 판정 근거
        }

    판정 기준:
    - final_score > 70: HIGH_RISK (red) → "고위험"
    - 50 < final_score <= 70: MEDIUM_RISK (orange) → "중위험"
    - final_score <= 50: LOW_RISK (green) → "저위험"
    """

    # 최종 통합 점수 계산
    final_integrated_score = (financial_risk_score * 0.6) + (qualitative_risk_score * 0.4)

    # 최종 등급 및 색상 결정
    if final_integrated_score > 70:
        final_risk_grade = "HIGH_RISK"
        color = "red"
        grade_label = "고위험"
    elif final_integrated_score > 50:
        final_risk_grade = "MEDIUM_RISK"
        color = "orange"
        grade_label = "중위험"
    else:
        final_risk_grade = "LOW_RISK"
        color = "green"
        grade_label = "저위험"

    # 설명 생성
    explanation = (
        f"정량 위험도: {financial_risk_score:.1f}/100, "
        f"정성 위험도: {qualitative_risk_score:.1f}/100을 "
        f"종합(정량 60% + 정성 40%)하여 최종 등급 【{grade_label}】으로 판정됩니다."
    )

    return {
        "final_integrated_score": round(final_integrated_score, 1),
        "final_risk_grade": final_risk_grade,
        "color": color,
        "explanation": explanation
    }

# ============================================================================
# Tab 4: 리스크 시나리오 분석 (스트레스 테스트)
# ============================================================================

def scenario_stress_test(financial_data: dict, scenario: str) -> dict:
    """
    과거 위기 시나리오에 충격 계수를 적용하여 스트레스 테스트를 수행합니다.

    각 시나리오별로 재무 지표에 충격을 적용하고, 변화된 Z-Score를 계산합니다.

    Args:
        financial_data: Node 1에서 추출한 재무 데이터 dict
            {
                "debt_ratio": 부채비율(%),
                "liquidity_ratio": 유동비율(%),
                "ar_turnover": 매출채권 회전율(배),
                "operating_cash_flow": 영업현금흐름(원),
                "net_income": 순이익(원),
                ...
            }
        scenario: "crisis_2008" | "covid19" | "rate_hike" | "industry_decline"

    Returns:
        {
            "scenario": str,                      # 선택된 시나리오
            "scenario_name": str,                 # 시나리오 한글명
            "shocked_metrics": dict,              # 충격 적용된 지표들
            "original_z_score": float,            # 기존 Z-Score
            "shocked_z_score": float,             # 시나리오 적용 후 Z-Score
            "resilience": str,                    # "견딜 수 있음" | "위험" | "심각"
            "change_percentage": float,           # Z-Score 변화율(%)
            "recommendation": str                 # 결론 및 권고사항
        }

    시나리오별 충격 계수:
    - crisis_2008: debt_ratio +30%, liquidity_ratio -30%
    - covid19: operating_cash_flow -40%, net_income -35%
    - rate_hike: liquidity_ratio -20%, interest_expense +50%
    - industry_decline: operating_cash_flow -30%, net_income -25%

    Z-Score 판정 기준:
    - Z > 2.99: "견딜 수 있음" (안전)
    - 1.81 < Z <= 2.99: "위험" (그레이존)
    - Z <= 1.81: "심각" (위기)
    """

    # 시나리오별 충격 계수 (곱하기 방식)
    shock_scenarios = {
        "crisis_2008": {
            "debt_ratio": 1.3,             # +30%
            "liquidity_ratio": 0.7,        # -30%
            "ar_turnover": 0.9,            # -10%
            "operating_cash_flow": 0.8,    # -20%
            "net_income": 0.7              # -30%
        },
        "covid19": {
            "debt_ratio": 1.1,             # +10%
            "liquidity_ratio": 0.85,       # -15%
            "ar_turnover": 0.9,            # -10%
            "operating_cash_flow": 0.6,    # -40%
            "net_income": 0.65             # -35%
        },
        "rate_hike": {
            "debt_ratio": 1.15,            # +15%
            "liquidity_ratio": 0.8,        # -20%
            "ar_turnover": 0.95,           # -5%
            "operating_cash_flow": 0.9,    # -10%
            "net_income": 0.85             # -15%
        },
        "industry_decline": {
            "debt_ratio": 1.1,             # +10%
            "liquidity_ratio": 0.85,       # -15%
            "ar_turnover": 0.85,           # -15%
            "operating_cash_flow": 0.7,    # -30%
            "net_income": 0.75             # -25%
        }
    }

    scenario_names = {
        "crisis_2008": "2008년 금융위기",
        "covid19": "COVID-19 팬데믹",
        "rate_hike": "금리 상승",
        "industry_decline": "산업 침체"
    }

    if scenario not in shock_scenarios:
        return {"error": f"Unknown scenario: {scenario}"}

    shocks = shock_scenarios[scenario]
    scenario_name = scenario_names.get(scenario, scenario)

    # 기존 Z-Score 계산
    original_z_score = _calculate_z_score_from_financial_data(financial_data)

    # 충격 계수 적용하여 shocked_metrics 생성
    shocked_metrics = {}
    for key, value in financial_data.items():
        if key in shocks and value is not None:
            shocked_metrics[key] = value * shocks[key]
        else:
            shocked_metrics[key] = value

    # 변화된 Z-Score 계산
    shocked_z_score = _calculate_z_score_from_financial_data(shocked_metrics)

    # Z-Score 변화율 계산
    if original_z_score > 0:
        change_percentage = ((shocked_z_score - original_z_score) / original_z_score) * 100
    else:
        change_percentage = 0

    # Resilience 판정
    if shocked_z_score > 2.99:
        resilience = "견딜 수 있음"
        resilience_detail = "기업은 이 위기 상황에서 충분한 회복력을 보유하고 있습니다."
    elif shocked_z_score > 1.81:
        resilience = "위험"
        resilience_detail = "기업의 재무 건강도가 악화되어 주의가 필요합니다."
    else:
        resilience = "심각"
        resilience_detail = "기업은 이 위기 상황에서 심각한 재무 어려움에 직면할 수 있습니다."

    # 권고사항 생성
    recommendation = (
        f"【{scenario_name}】 시나리오 스트레스 테스트 결과:\n\n"
        f"▸ 기존 Z-Score: {original_z_score:.2f}\n"
        f"▸ 시나리오 적용 후 Z-Score: {shocked_z_score:.2f}\n"
        f"▸ 변화율: {change_percentage:+.1f}%\n"
        f"▸ 회복력 평가: 【{resilience}】\n\n"
        f"{resilience_detail}\n\n"
        f"기업은 다음과 같은 사항을 점검하시기 바랍니다:\n"
        f"① 부채 관리 및 이자비용 커버율 개선\n"
        f"② 운영현금흐름 안정성 확보\n"
        f"③ 유동성 버퍼(현금성자산) 확충\n"
        f"④ 매출채권 관리 개선"
    )

    return {
        "scenario": scenario,
        "scenario_name": scenario_name,
        "shocked_metrics": shocked_metrics,
        "original_z_score": round(original_z_score, 2),
        "shocked_z_score": round(shocked_z_score, 2),
        "resilience": resilience,
        "change_percentage": round(change_percentage, 1),
        "recommendation": recommendation
    }


def _calculate_z_score_from_financial_data(financial_data: dict) -> float:
    """
    재무 데이터로부터 Z-Score를 계산합니다.

    Node 1의 financial_rule_engine() 로직을 기반으로 risk_scores를 계산하고,
    이를 Z-Score(0-4 범위)로 변환합니다.

    Args:
        financial_data: 재무 지표 dict

    Returns:
        float: Z-Score (0-4 범위)
    """

    risk_scores = {
        "revenue_quality": 20,
        "liquidity_stress": 20,
        "leverage_risk": 20,
    }

    # Revenue Quality 점수 계산
    try:
        ar_turnover = financial_data.get("ar_turnover")
        ocf = financial_data.get("operating_cash_flow")

        revenue_quality_score = 20

        if ar_turnover is not None:
            if ar_turnover < 2:
                revenue_quality_score = 70
            elif ar_turnover < 4:
                revenue_quality_score = 50
            else:
                revenue_quality_score = 20

        if ocf is not None and ocf < 0:
            revenue_quality_score = max(revenue_quality_score, 85)

        risk_scores["revenue_quality"] = revenue_quality_score
    except:
        pass

    # Liquidity Stress 점수 계산
    try:
        liquidity_ratio = financial_data.get("liquidity_ratio")

        liquidity_score = 20

        if liquidity_ratio is not None:
            if liquidity_ratio < 100:
                liquidity_score = 90
            elif liquidity_ratio < 150:
                liquidity_score = 60
            else:
                liquidity_score = 20

        risk_scores["liquidity_stress"] = liquidity_score
    except:
        pass

    # Leverage Risk 점수 계산
    try:
        debt_ratio = financial_data.get("debt_ratio")

        leverage_score = 20

        if debt_ratio is not None:
            if debt_ratio > 200:
                leverage_score = 80
            elif debt_ratio > 160:
                leverage_score = 50
            else:
                leverage_score = 20

        risk_scores["leverage_risk"] = leverage_score
    except:
        pass

    # 종합 financial_risk_score 계산 (0-100)
    financial_risk_score = (
        risk_scores["revenue_quality"] * 0.40 +
        risk_scores["liquidity_stress"] * 0.35 +
        risk_scores["leverage_risk"] * 0.25
    )

    # Z-Score로 변환 (0-4 범위)
    # risk_score 0 → z_score 4 (안전)
    # risk_score 100 → z_score 0 (위기)
    z_score = 4 - (financial_risk_score / 25)

    return z_score

# ============================================================================
# 연도별 재무 위험도 추세 조회 (5년 실제 데이터)
# ============================================================================

@st.cache_data(ttl=3600)
def get_financial_risk_trend(_dart, corp_code):
    """
    5년간(2020-2024)의 실제 재무 위험도 추세를 조회합니다.

    Args:
        dart: OpenDartReader 인스턴스
        corp_code: 기업 코드

    Returns:
        dict: {
            2020: 35.2,
            2021: 38.5,
            2022: 40.1,
            2023: 42.3,
            2024: 32.0,
            "status": "완료 | 부분 | 오류"
        }
    """

    import time

    trend_scores = {}
    years = [2020, 2021, 2022, 2023, 2024]
    success_count = 0
    error_count = 0

    for year in years:
        try:
            year_str = str(year)

            # DART에서 해당 연도 재무제표 조회
            fs_data = _dart.finstate_all(corp_code, year_str)

            if fs_data is None or fs_data.empty:
                trend_scores[year] = None
                error_count += 1
            else:
                # 위험도 점수 계산 (financial_rule_engine 재사용)
                analysis = financial_rule_engine(fs_data)
                trend_scores[year] = round(analysis['financial_risk_score'], 1)
                success_count += 1

            # API 호출 제한 회피 (연도별 1초 대기)
            time.sleep(1)

        except Exception as e:
            # 개별 연도 오류는 무시하고 계속 진행
            trend_scores[year] = None
            error_count += 1

    # 조회 상태 판정
    if success_count == 5:
        status = "완료"
    elif success_count > 0:
        status = "부분"
    else:
        status = "오류"

    trend_scores["status"] = status
    return trend_scores

# ============================================================================
# UI - 사이드바 공통 (제거됨)
# ============================================================================

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

    # 정성 점수 계산
    qualitative_risk = extract_qualitative_risk_score(risk_categories)

    # 최종 통합 점수 계산
    final_risk = integrate_final_risk_grade(
        analysis['financial_risk_score'],
        qualitative_risk['qualitative_risk_score']
    )

    # 5년 실제 위험도 추세 조회 (DART 기반)
    trend_scores = None
    with st.spinner("5년 위험도 추세 조회 중... (최초 1회만 수행)"):
        try:
            trend_scores = get_financial_risk_trend(dart, corp_code)
        except Exception as e:
            st.warning(f"추세 데이터 조회 오류: {e}")
            trend_scores = None

    tab1, tab2, tab3, tab4 = st.tabs(["종합 리스크 대시보드", "정량 재무 분석", "정성적 크로스체킹", "리스크 시나리오"])

    # ========================================================================
    # Tab 1: 종합 리스크 대시보드 (통합 대시보드)
    # ========================================================================
    with tab1:
        st.markdown('<div class="section-header">최종 위험 평가</div>', unsafe_allow_html=True)

        # 기업 기본 정보
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

        # [상단] 최종 위험 등급 강조 표시
        final_score = final_risk['final_integrated_score']
        final_grade = final_risk['final_risk_grade']
        color = final_risk['color']

        color_map = {
            "red": "#c41c3b",
            "orange": "#f57c00",
            "green": "#2e7d32"
        }

        grade_map = {
            "HIGH_RISK": "고위험",
            "MEDIUM_RISK": "중위험",
            "LOW_RISK": "저위험"
        }

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba({int(color_map[color][1:3], 16)}, {int(color_map[color][3:5], 16)}, {int(color_map[color][5:7], 16)}, 0.1) 0%, rgba({int(color_map[color][1:3], 16)}, {int(color_map[color][3:5], 16)}, {int(color_map[color][5:7], 16)}, 0.05) 100%);
                    border-left: 5px solid {color_map[color]};
                    padding: 24px;
                    border-radius: 8px;
                    margin: 20px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <p style="font-size: 1.2em; font-weight: 600; margin: 0; color: #1b4332;">최종 위험 등급</p>
                    <p style="font-size: 2.5em; font-weight: 700; margin: 10px 0 0 0; color: {color_map[color]};">{grade_map[final_grade]}</p>
                </div>
                <div style="text-align: right;">
                    <p style="font-size: 3em; font-weight: 700; color: {color_map[color]}; margin: 0;">{final_score}</p>
                    <p style="font-size: 1em; color: #666; margin: 5px 0 0 0;">/100</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(final_risk['explanation'])
        st.markdown("")

        # [중단] 정량 vs 정성 비교
        st.markdown('<div class="section-header">정량 vs 정성 위험도 비교</div>', unsafe_allow_html=True)

        col_quant, col_qual = st.columns(2)

        with col_quant:
            with st.container(border=True):
                st.markdown("### 📊 정량 위험도")
                st.metric(
                    "재무 지표 기반",
                    f"{analysis['financial_risk_score']:.1f}",
                    help="부채비율, 유동성, 현금흐름 등 정량 지표"
                )
                st.caption(f"평가: {analysis['risk_level']}")

                # 정량 위험도 구성 검증
                revenue_score = analysis['component_scores']['revenue_quality']
                liquidity_score = analysis['component_scores']['liquidity_stress']
                leverage_score = analysis['component_scores']['leverage_risk']
                final_score = analysis['financial_risk_score']

                st.caption(
                    f"💡 **정량 위험도 구성 (가중치)**:\n"
                    f"   • 매출채권 회전율: {revenue_score:.0f}점 (40%)\n"
                    f"   • 유동비율: {liquidity_score:.0f}점 (35%)\n"
                    f"   • 부채비율: {leverage_score:.0f}점 (25%)\n"
                    f"   • 최종 점수: {final_score:.1f} = "
                    f"({revenue_score:.0f} × 0.40) + ({liquidity_score:.0f} × 0.35) + ({leverage_score:.0f} × 0.25)"
                )

        with col_qual:
            with st.container(border=True):
                st.markdown("### 📋 정성 위험도")
                st.metric(
                    "공시 주석 기반",
                    f"{qualitative_risk['qualitative_risk_score']:.1f}",
                    help="소송, 특수관계자거래, 자산손상 등"
                )
                st.caption(f"발견된 리스크 카테고리: {qualitative_risk['risk_count']}개")

                # 정성 점수 검증 정보
                breakdown = qualitative_risk['risk_breakdown']
                con_liab = breakdown.get('contingent_liabilities', 0)
                rel_party = breakdown.get('related_party_transactions', 0)
                asset_imp = breakdown.get('asset_impairment', 0)

                st.caption(f"📐 우발채무 & 소송: {con_liab}개")
                st.caption(f"📐 특수관계자거래: {rel_party}개")
                st.caption(f"📐 자산손상: {asset_imp}개")

                # 개선된 점수 계산식 설명
                assessment = breakdown.get('investment_assessment', 0)
                calc_details = (
                    f"💡 **점수 계산식:**\n"
                    f"   ({con_liab}개 × 15) + ({rel_party}개 × 20) + ({asset_imp}개 × 20) + "
                    f"(평가{'있음' if assessment else '없음'}: {25 if assessment else 0}점)\n"
                    f"   = {con_liab*15} + {rel_party*20} + {asset_imp*20} + {25 if assessment else 0} "
                    f"= **{qualitative_risk['qualitative_risk_score']:.1f}점**"
                )
                st.caption(calc_details)

        st.markdown("")
        st.markdown("---")

        # [중단] 지난 5년 위험도 추세 (DART 실제 데이터)
        st.markdown('<div class="section-header">📈 지난 5년 위험도 추세 (DART 공시 기반 실제 데이터)</div>', unsafe_allow_html=True)

        try:
            import pandas as pd
            import plotly.graph_objects as go

            # 실제 데이터 조회 여부 확인
            has_real_data = trend_scores is not None and trend_scores.get("status") != "오류"

            if has_real_data:
                # 실제 DART 데이터로 그래프 생성
                years = [2020, 2021, 2022, 2023, 2024]
                scores = []
                valid_years = []

                for year in years:
                    score = trend_scores.get(year)
                    if score is not None:
                        scores.append(score)
                        valid_years.append(year)

                if len(valid_years) > 0:
                    # Plotly 인터랙티브 그래프
                    fig = go.Figure()

                    # 실제 데이터 라인
                    fig.add_trace(go.Scatter(
                        x=valid_years,
                        y=scores,
                        mode='lines+markers',
                        name='위험도 추세',
                        line=dict(color='#2d6a4f', width=3),
                        marker=dict(size=10, color='#2d6a4f'),
                        hovertemplate='<b>%{x}년</b><br>위험도: %{y:.1f}<extra></extra>'
                    ))

                    # 최신 연도 강조 (2024)
                    if 2024 in valid_years:
                        idx = valid_years.index(2024)
                        fig.add_trace(go.Scatter(
                            x=[2024],
                            y=[scores[idx]],
                            mode='markers+text',
                            name='최신 데이터 (2024)',
                            marker=dict(size=16, color='#c41c3b', symbol='star',
                                       line=dict(color='#1b4332', width=2)),
                            text=['최신'],
                            textposition='top center',
                            textfont=dict(color='#c41c3b', size=12),
                            hovertemplate='<b>2024 (최신)</b><br>위험도: %{y:.1f}<extra></extra>'
                        ))

                    # 레이아웃 설정
                    fig.update_layout(
                        title='',
                        xaxis_title='연도',
                        yaxis_title='위험도 점수 (0-100)',
                        hovermode='x unified',
                        template='plotly_white',
                        height=340,
                        showlegend=True,
                        legend=dict(x=0.02, y=0.98),
                        yaxis=dict(range=[0, 100]),
                        xaxis=dict(tickmode='linear', tick0=2020, dtick=1),
                        margin=dict(l=60, r=60, t=20, b=60),
                        font=dict(family="Pretendard, sans-serif")
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 그래프 설명
                    st.success(
                        "✅ **DART 공시 기반 실제 데이터입니다**\n\n"
                        "📊 본 그래프는 연도별 DART 공시 재무제표에서 추출한 실제 위험도 추세입니다.\n"
                        "💡 각 연도의 위험도 변화 추이를 통해 기업의 재무 건전성 개선/악화 추세를 확인할 수 있습니다."
                    )

                    # 조회 상태 표시
                    if trend_scores.get("status") == "부분":
                        st.warning(f"⚠️ 일부 연도의 데이터를 조회하지 못했습니다. (조회 완료: {len(valid_years)}/5년)")
                else:
                    st.warning("📊 그래프를 표시할 유효한 데이터가 없습니다.")
            else:
                # 실제 데이터 조회 실패
                st.warning(
                    "⚠️ **DART 5년 데이터 조회 실패**\n\n"
                    "현재 DART API에서 과거 연도 재무제표를 모두 조회할 수 없었습니다.\n"
                    "현재 2024년 데이터만 사용 중입니다.\n\n"
                    "과거 5년 추이를 확인하려면:\n"
                    "1. DART 웹사이트 방문 (dart.fss.or.kr)\n"
                    "2. 기업명으로 검색\n"
                    "3. 연도별 공시 보고서에서 위험도 지표 확인"
                )

        except Exception as e:
            st.error(f"그래프 생성 오류: {e}")

        st.markdown("")
        st.markdown("---")

        # [하단] 주요 위험 요인
        st.markdown('<div class="section-header">주요 위험 요인</div>', unsafe_allow_html=True)

        risk_data = risk_categories

        with st.container(border=True):
            col_risks1, col_risks2 = st.columns(2)

            with col_risks1:
                st.subheader("우발채무 & 소송")
                if risk_data["contingent_liabilities"]:
                    for item in risk_data["contingent_liabilities"][:3]:
                        st.caption(f"⚠️ {item}")
                else:
                    st.caption("✓ 확인된 항목 없음")

                st.subheader("특수관계자 거래")
                if risk_data["related_party_transactions"]:
                    for item in risk_data["related_party_transactions"][:3]:
                        st.caption(f"⚠️ {item}")
                else:
                    st.caption("✓ 확인된 항목 없음")

            with col_risks2:
                st.subheader("자산손상 & 투자손실")
                if risk_data["asset_impairment"]:
                    for item in risk_data["asset_impairment"][:3]:
                        st.caption(f"⚠️ {item}")
                else:
                    st.caption("✓ 확인된 항목 없음")

                st.subheader("정성 평가")
                if risk_data["investment_assessment"]:
                    st.caption(risk_data["investment_assessment"][:150] + "...")
                else:
                    st.caption("✓ 확인된 항목 없음")

        st.markdown("")
        st.markdown("---")

        # [하단] 조기 경보
        st.markdown('<div class="section-header">⚡ 조기 경보</div>', unsafe_allow_html=True)

        if final_score > 70:
            st.error(
                "🚨 **고위험 판정**\n\n"
                "정량 및 정성 분석 결과 이 기업은 현저한 재무 리스크를 보유하고 있습니다. "
                "즉시적인 재무 상태 점검 및 추가 실사(Due Diligence)를 권장합니다."
            )
        elif final_score > 50:
            st.warning(
                "⚠️ **중위험 판정**\n\n"
                "특정 재무 지표 및 공시 항목에서 주의가 필요합니다. "
                "경영진의 개선 계획 및 공시 주석을 면밀히 검토하시기 바랍니다."
            )
        else:
            st.success(
                "✅ **저위험 판정**\n\n"
                "정량 및 정성 분석상 기업의 재무 건전성은 양호한 수준입니다. "
                "다만 정기적인 모니터링을 권장드립니다."
            )

    # ========================================================================
    # Tab 2: 정량 재무 분석
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-header">정량 규칙 엔진 기반 회계 리스크 점수</div>', unsafe_allow_html=True)

        # 상세 지표
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            risk_score = analysis['financial_risk_score']
            st.metric(
                "정량 위험도",
                f"{risk_score:.1f}",
                delta=analysis['risk_level'],
                delta_color="inverse",
                help="높을수록 리스크가 높음"
            )

        with col2:
            st.metric(
                "매출 질 점수",
                f"{analysis['component_scores']['revenue_quality']:.0f}",
                help="매출채권 회전율, 영업현금흐름"
            )

        with col3:
            st.metric(
                "유동성 점수",
                f"{analysis['component_scores']['liquidity_stress']:.0f}",
                help="단기유동성 압박도"
            )

        with col4:
            st.metric(
                "부채 점수",
                f"{analysis['component_scores']['leverage_risk']:.0f}",
                help="부채비율 및 자본 구조"
            )

        st.markdown("")
        st.markdown("---")

        # 안정성 지표 섹션 (부채비율, 유동비율)
        st.markdown('<div class="section-header">안정성 지표</div>', unsafe_allow_html=True)

        col_stability1, col_stability2 = st.columns(2)

        with col_stability1:
            with st.container(border=True):
                st.markdown("### 부채비율 (Debt Ratio)")
                debt_ratio_value = analysis.get('debt_ratio')
                if debt_ratio_value is not None:
                    st.metric(
                        "비율",
                        f"{debt_ratio_value:.2f}%",
                        help="부채 / 자기자본 × 100\n낮을수록 좋음\n일반적 정상범위: 100-200%"
                    )
                    if debt_ratio_value > 200:
                        st.error("부채비율이 높은 수준입니다. 부채 관리 개선이 필요합니다.")
                    elif debt_ratio_value > 160:
                        st.warning("부채비율이 주의 수준입니다.")
                    else:
                        st.success("부채비율이 정상 수준입니다.")
                else:
                    st.caption("💡 재무 데이터를 조회하지 못했습니다.")

        with col_stability2:
            with st.container(border=True):
                st.markdown("### 유동비율 (Current Ratio)")
                current_ratio_value = analysis.get('current_ratio')
                if current_ratio_value is not None:
                    st.metric(
                        "비율",
                        f"{current_ratio_value:.2f}%",
                        help="유동자산 / 유동부채 × 100\n높을수록 좋음\n일반적 정상범위: 100% 이상"
                    )
                    if current_ratio_value < 100:
                        st.error("유동비율이 낮아 단기유동성이 부족합니다.")
                    elif current_ratio_value < 150:
                        st.warning("유동비율이 주의 수준입니다.")
                    else:
                        st.success("유동비율이 양호한 수준입니다.")
                else:
                    st.caption("💡 재무 데이터를 조회하지 못했습니다.")

        st.markdown("")
        st.markdown("---")

        # 수익성 지표 섹션
        st.markdown('<div class="section-header">수익성 지표</div>', unsafe_allow_html=True)

        try:
            if financial_df is not None:
                net_income = find_account_value(financial_df, ['순이익', '당기순이익', 'net_income']) or 1
                total_assets = find_account_value(financial_df, ['자산총계', '총자산']) or 1

                # 자기자본 찾기 (우선순위: 자기자본총계 → 주주자본 → 자산-부채 → 자본금)
                equity = (
                    find_account_value(financial_df, ['자기자본 총계', '자기자본합계']) or
                    find_account_value(financial_df, ['주주자본 총계', '주주자본합계']) or
                    find_account_value(financial_df, ['자기자본', '주주자본']) or
                    None
                )

                # 자기자본을 못 찾으면 자산 - 부채로 계산
                if not equity:
                    total_debt = find_account_value(financial_df, ['부채총계', '총부채'])
                    if total_debt:
                        equity = total_assets - total_debt

                # 그래도 못 찾으면 자본금 사용 (권장되지 않음)
                if not equity:
                    equity = find_account_value(financial_df, ['자본금'])

                equity = equity or 1

                roe = (net_income / equity * 100) if equity > 0 else 0
                roa = (net_income / total_assets * 100) if total_assets > 0 else 0
            else:
                roe = 0
                roa = 0
        except:
            roe = 0
            roa = 0

        # 등급 판정 함수
        def get_profitability_grade(value, metric_type="roe"):
            if metric_type == "roe":
                if value > 15:
                    return "우수", "🟢"
                elif value >= 10:
                    return "정상", "🔵"
                else:
                    return "낮음", "🟠"
            else:  # roa
                if value > 5:
                    return "우수", "🟢"
                elif value >= 2:
                    return "정상", "🔵"
                else:
                    return "낮음", "🟠"

        roe_grade, roe_emoji = get_profitability_grade(roe, "roe")
        roa_grade, roa_emoji = get_profitability_grade(roa, "roa")

        col_roe, col_roa = st.columns(2)

        with col_roe:
            with st.container(border=True):
                st.markdown("### ROE (자기자본수익률)")
                st.metric(
                    "수익률",
                    f"{roe:.2f}%",
                    help="순이익 / 자기자본 × 100\n높을수록 좋음\n(자기자본 = 자본금 + 잉여금 등)"
                )
                st.markdown(f"**평가:** {roe_emoji} {roe_grade}")
                if roe > 15:
                    st.success("자기자본 대비 수익성이 우수합니다.")
                elif roe >= 10:
                    st.info("자기자본 대비 수익성이 정상 수준입니다.")
                else:
                    st.warning("자기자본 대비 수익성이 낮습니다.")

                # ROE 검증 정보
                try:
                    net_income_roe = find_account_value(financial_df, ['순이익', '당기순이익', 'net_income']) or 0
                    equity_roe = find_account_value(financial_df, ['자기자본 총계', '자기자본합계']) or find_account_value(financial_df, ['자기자본']) or 1
                    st.caption(f"📐 계산식: 순이익 / 자기자본 × 100")
                    st.caption(f"💡 값: {net_income_roe:,.0f}원 / {equity_roe:,.0f}원 × 100")
                except:
                    pass

        with col_roa:
            with st.container(border=True):
                st.markdown("### ROA (자산수익률)")
                st.metric(
                    "수익률",
                    f"{roa:.2f}%",
                    help="순이익 / 총자산 × 100\n높을수록 좋음"
                )
                st.markdown(f"**평가:** {roa_emoji} {roa_grade}")
                if roa > 5:
                    st.success("자산 활용 효율이 우수합니다.")
                elif roa >= 2:
                    st.info("자산 활용 효율이 정상 수준입니다.")
                else:
                    st.warning("자산 활용 효율이 낮습니다.")

                # ROA 검증 정보
                try:
                    net_income_roa = find_account_value(financial_df, ['순이익', '당기순이익', 'net_income']) or 0
                    total_assets_roa = find_account_value(financial_df, ['자산총계', '총자산']) or 1
                    st.caption(f"📐 계산식: 순이익 / 총자산 × 100")
                    st.caption(f"💡 값: {net_income_roa:,.0f}원 / {total_assets_roa:,.0f}원 × 100")
                except:
                    pass

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

        st.markdown('<div class="section-header">정량 리스크 평가</div>', unsafe_allow_html=True)

        with st.container(border=True):
            risk_score = analysis['financial_risk_score']

            if risk_score >= 70:
                assessment = "현재 정량 지표상 상당한 재무 리스크가 식별됩니다. 부채비율, 유동성, 현금흐름 등의 주요 지표에서 개선이 필요합니다. 추가적인 정성 분석을 통해 이러한 위험 요소가 기업의 구조적 문제인지, 또는 일시적 변동인지 파악해야 합니다."
            elif risk_score >= 50:
                assessment = "정량 지표상 중간 수준의 리스크가 식별됩니다. 특정 회계 지표에서 주의가 필요하며, 경영진의 대응 방안 및 개선 계획을 검토할 필요가 있습니다. 정성 분석을 통해 경영 안정성을 추가 확인하십시오."
            else:
                assessment = "정량 지표상 위험도는 정상 수준입니다. 다만, 주석 정보와의 종합 검토를 통해 잠재적 리스크가 있는지 추가 확인이 권장됩니다."

            st.markdown(assessment)

        st.markdown("")
        st.markdown("---")

        # 정성 점수 추가
        st.markdown('<div class="section-header">정성 위험도 보완 지표</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.metric(
                "정성 위험도 점수",
                f"{qualitative_risk['qualitative_risk_score']:.1f}",
                help="공시 주석에서 발견된 우발채무, 특수관계자거래, 자산손상 등"
            )
            st.caption(f"발견된 리스크 카테고리: {qualitative_risk['risk_count']}개")
            st.caption(f"카테고리별 분석:")

            breakdown = qualitative_risk['risk_breakdown']
            col_breakdown1, col_breakdown2 = st.columns(2)

            with col_breakdown1:
                st.caption(f"• 우발채무 & 소송: {breakdown.get('contingent_liabilities', 0)}개")
                st.caption(f"• 특수관계자거래: {breakdown.get('related_party_transactions', 0)}개")

            with col_breakdown2:
                st.caption(f"• 자산손상 & 투자손실: {breakdown.get('asset_impairment', 0)}개")
                st.caption(f"• 최종 평가: {'있음' if breakdown.get('investment_assessment', 0) else '없음'}")

            # 개선된 정성 점수 계산식 설명
            st.markdown("")
            con_liab = breakdown.get('contingent_liabilities', 0)
            rel_party = breakdown.get('related_party_transactions', 0)
            asset_imp = breakdown.get('asset_impairment', 0)
            assessment = breakdown.get('investment_assessment', 0)

            calc_formula = (
                f"**📊 점수 계산식:**\n\n"
                f"({con_liab}개 × 15점) + ({rel_party}개 × 20점) + ({asset_imp}개 × 20점) + "
                f"(평가{'있음' if assessment else '없음'}: {25 if assessment else 0}점)\n\n"
                f"= {con_liab*15} + {rel_party*20} + {asset_imp*20} + {25 if assessment else 0} "
                f"= **{qualitative_risk['qualitative_risk_score']:.1f}점**"
            )
            st.caption(calc_formula)

    # ========================================================================
    # Tab 3: 정성적 크로스체킹
    # ========================================================================
    with tab3:
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
    # Tab 4: 리스크 시나리오 분석
    # ========================================================================
    with tab4:
        st.markdown('<div class="section-header">스트레스 테스트: 위기 시나리오 분석</div>', unsafe_allow_html=True)

        st.markdown("과거 위기 시나리오를 적용했을 때 기업의 재무 회복력을 평가합니다.")
        st.markdown("")

        # 시나리오 선택
        scenario_options = {
            "crisis_2008": "2008년 금융위기",
            "covid19": "COVID-19 팬데믹",
            "rate_hike": "금리 상승",
            "industry_decline": "산업 침체"
        }

        selected_scenario = st.selectbox(
            "위기 시나리오를 선택하세요",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
            key="scenario_select"
        )

        st.markdown("")

        # 재무 데이터 준비 (Node 1 분석 결과에서 추출)
        try:
            if financial_df is not None:
                sales = find_account_value(financial_df, ['매출액', '매출', 'revenue']) or 1
                ar = find_account_value(financial_df, ['매출채권', '기타채권']) or 1
                ocf = find_account_value(financial_df, ['영업활동', '영업현금']) or 0
                current_assets = find_account_value(financial_df, ['유동자산']) or 1
                current_liabilities = find_account_value(financial_df, ['유동부채']) or 1
                total_assets = find_account_value(financial_df, ['자산총계']) or 1
                total_debt = find_account_value(financial_df, ['부채총계']) or 1

                debt_ratio = (total_debt / (total_assets - total_debt) * 100) if (total_assets - total_debt) > 0 else 100
                liquidity_ratio = (current_assets / current_liabilities * 100) if current_liabilities > 0 else 100
                ar_turnover = (sales / ar) if ar > 0 else 2

                financial_data = {
                    "debt_ratio": debt_ratio,
                    "liquidity_ratio": liquidity_ratio,
                    "ar_turnover": ar_turnover,
                    "operating_cash_flow": ocf,
                    "net_income": 0
                }
            else:
                raise ValueError("재무 데이터 없음")
        except:
            financial_data = {
                "debt_ratio": 100,
                "liquidity_ratio": 150,
                "ar_turnover": 4.0,
                "operating_cash_flow": 0,
                "net_income": 0
            }

        # 스트레스 테스트 실행
        stress_result = scenario_stress_test(financial_data, selected_scenario)

        # 결과 표시
        st.markdown(f"**시나리오: {stress_result['scenario_name']}**")
        st.markdown("")

        # 기존 vs 변화된 Z-Score 비교
        col_z1, col_z2, col_z3 = st.columns(3)

        with col_z1:
            st.metric(
                "기존 Z-Score",
                f"{stress_result['original_z_score']:.2f}",
                help="시나리오 적용 전"
            )

        with col_z2:
            st.metric(
                "변화된 Z-Score",
                f"{stress_result['shocked_z_score']:.2f}",
                help="시나리오 적용 후"
            )

        with col_z3:
            st.metric(
                "변화율",
                f"{stress_result['change_percentage']:+.1f}%",
                help="Z-Score 변화 %"
            )

        st.markdown("")
        st.markdown("---")

        # Resilience 판정
        resilience = stress_result['resilience']
        resilience_colors = {
            "견딜 수 있음": "green",
            "위험": "orange",
            "심각": "red"
        }

        st.markdown(f"### 🎯 회복력 평가: **{resilience}**")

        if resilience == "견딜 수 있음":
            st.success("기업은 이 위기 상황에서 충분한 회복력을 보유하고 있습니다.")
        elif resilience == "위험":
            st.warning("기업의 재무 건강도가 악화되어 주의가 필요합니다.")
        else:
            st.error("기업은 이 위기 상황에서 심각한 재무 어려움에 직면할 수 있습니다.")

        st.markdown("")
        st.markdown("---")

        # 권고사항
        st.markdown('<div class="section-header">권고사항</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(stress_result['recommendation'])
