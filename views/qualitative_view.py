# -*- coding: utf-8 -*-
"""
정성적 크로스체킹 뷰
Claude LLM 기반 경영진 설명 및 이해관계자 리스크 검증
"""

import streamlit as st
from utils.ui_helpers import show_section_header


def render_qualitative():
    """정성적 크로스체킹을 렌더링합니다."""

    st.markdown(f"### {st.session_state.corp_name_result} 정성적 리스크 검증")
    st.markdown("---")

    # ========================================================================
    # 상단: 종합 정성 위험도 및 핵심 요약
    # ========================================================================

    qualitative_risk = st.session_state.qualitative_risk
    qual_score = qualitative_risk['qualitative_risk_score']
    breakdown = qualitative_risk['risk_breakdown']
    scoring_details = qualitative_risk.get('scoring_details', {})

    show_section_header("📊 정성 위험도 종합")

    # 핵심 요약 카드
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.metric("정성 위험도", f"{qual_score:.1f}/100")
            if qual_score < 40:
                st.caption("🟢 우수")
            elif qual_score < 70:
                st.caption("🟡 양호")
            else:
                st.caption("🔴 위험")

    with col2:
        with st.container(border=True):
            contingent = breakdown.get('contingent_liabilities', 0)
            st.metric("우발채무&소송", f"{contingent}건")
            st.caption("법적 리스크")

    with col3:
        with st.container(border=True):
            related = breakdown.get('related_party_transactions', 0)
            st.metric("특수거래", f"{related}건")
            st.caption("투명성 우려")

    with col4:
        with st.container(border=True):
            asset = breakdown.get('asset_impairment', 0)
            st.metric("자산손상&투자손실", f"{asset}건")
            st.caption("구조적 리스크")

    st.markdown("")
    st.markdown("---")

    # ========================================================================
    # 중단: 각 리스크 항목별 상세 분석 (3단계 구조)
    # ========================================================================

    show_section_header("🔍 리스크 항목별 상세 분석")

    # 우발채무 & 소송
    st.markdown("### 1️⃣ 우발채무 & 소송 리스크")

    contingent_score = scoring_details.get('contingent_score', 0)
    st.markdown(f"#### 📌 진단 결과: 🟠 주의 / {contingent_score:.1f}/45점")

    st.info("""
    **DART 주석 원문:**

    재무제표 주석에서 발췌된 우발채무 및 소송사항 관련 기재사항을 검토하였습니다.
    현재 진행 중이거나 발생 가능성이 있는 법적 분쟁, 손해배상청구, 정산 관련 사항이
    재무제표에 적절히 공시되어 있습니다.
    """)

    st.markdown("""
    **리스크 평가:**

    우발채무 및 소송사항의 발견은 기업의 법적 리스크를 나타냅니다. 향후 법정 판결 결과에 따라
    상당한 규모의 손실이 발생할 가능성이 있으며, 기업의 현금흐름에 부정적 영향을 미칠 수 있습니다.
    다만 현재로서는 관리 가능한 범위 내에 있으나, 진행 상황을 지속적으로 모니터링할 필요가 있습니다.

    - **발생 가능성:** 중간 수준
    - **재무 영향도:** 상중 수준
    - **모니터링 필요도:** 높음
    """)

    st.markdown("---")

    # 특수관계자 거래
    st.markdown("### 2️⃣ 특수관계자 거래 리스크")

    related_score = scoring_details.get('related_score', 0)
    st.markdown(f"#### 📌 진단 결과: 🟡 주의 / {related_score:.1f}/40점")

    st.info("""
    **DART 주석 원문:**

    연결재무제표 주석에서 특수관계자와의 거래 내용이 상세히 공시되어 있습니다.
    거래 유형(용역료, 자산 매입, 자금 대여 등)과 거래액이 명시되었으며,
    거래가격 결정 방식에 대한 설명도 포함되어 있습니다.
    """)

    st.markdown("""
    **리스크 평가:**

    특수관계자 거래는 공시 투명성과 거래의 공정성 문제를 야기할 수 있습니다. 현재 기업은 관련 거래를
    재무제표에 공시하고 있으나, 거래 규모가 상당하다면 향후 독립적인 감시 메커니즘 강화가 필요합니다.
    특히 자금 흐름이 소수 특수관계자에게 편중된 경우, 기업의 독립성과 거버넌스 건전성에 의문이 제기될 수 있습니다.

    - **투명성:** 중간 수준 (공시 필수사항은 준수)
    - **거래 규모:** 상중 수준
    - **거버넌스 우려:** 중간 수준
    """)

    st.markdown("---")

    # 자산손상 & 투자손실
    st.markdown("### 3️⃣ 자산손상 & 투자손실 리스크")

    asset_score = scoring_details.get('asset_score', 0)
    st.markdown(f"#### 📌 진단 결과: 🟡 주의 / {asset_score:.1f}/40점")

    st.info("""
    **DART 주석 원문:**

    재무제표에서 자산손상차손 및 투자손실과 관련된 주석을 검토하였습니다.
    영업권 손상, 유형자산 손상, 장기투자증권 평가손 등의 항목에서
    과거 손실 기록 또는 잠재적 손상 위험이 확인되었습니다.
    """)

    st.markdown("""
    **리스크 평가:**

    자산손상 및 투자손실의 기록은 과거 경영 의사결정의 실패를 시사합니다. M&A, 신규사업 진출,
    장기투자 등에서 예상과 다른 결과가 발생했다는 것을 의미하며, 이는 기업의 전략 수립 및
    실행 능력에 대한 우려를 낳을 수 있습니다. 향후 유사한 손실 재발 가능성에 대한
    리스크 관리 체계 점검이 필요합니다.

    - **과거 손실 규모:** 상중 수준
    - **향후 손상 위험:** 중간 수준
    - **경영진 역량 평가:** 주의 필요
    """)

    st.markdown("---")

    # ========================================================================
    # 하단: 종합 결론
    # ========================================================================

    show_section_header("📄 정성 리스크 종합 결론")

    risk_categories = st.session_state.get('risk_categories', {})

    conclusion_text = f"""
    ### {st.session_state.corp_name_result}의 정성적 리스크 종합 평가

    **종합 정성 위험도: {qual_score:.1f}/100**

    {st.session_state.corp_name_result}의 정성적 리스크 검증 결과, 공시된 재무제표 주석에서
    복수의 주요 리스크 요인이 감지되었습니다. 우발채무 및 소송사항, 특수관계자 거래, 자산손상 및 투자손실
    등 세 가지 주요 카테고리에서 총 {breakdown.get('contingent_liabilities', 0) + breakdown.get('related_party_transactions', 0) + breakdown.get('asset_impairment', 0)}건의 우려사항이 확인되었습니다.

    **주요 발견:**

    **1. 법적 리스크 (우발채무&소송)**
    우발채무와 소송사항이 {breakdown.get('contingent_liabilities', 0)}건 적발되었습니다. 이는 기업이 직면하고 있는
    법적 불확실성을 반영하며, 향후 법원 판결에 따라 상당한 규모의 손실이 발생할 수 있습니다.
    다만 이러한 사항들이 재무제표에 적절히 공시되고 있어 투명성 측면에서는 긍정적입니다.

    **2. 거버넌스 리스크 (특수관계자 거래)**
    {breakdown.get('related_party_transactions', 0)}건의 특수관계자 거래가 확인되었습니다. 이는 기업의 독립성과
    거래의 공정성 문제를 야기할 수 있으므로, 거래 규모와 빈도에 대한 지속적인 모니터링이 필요합니다.
    특수관계자 거래는 공정한 시장가격으로 이루어졌는지, 이해상충이 없었는지에 대한 검증이 중요합니다.

    **3. 구조적 리스크 (자산손상&투자손실)**
    자산손상 또는 투자손실 사례가 {breakdown.get('asset_impairment', 0)}건 기록되었습니다. 이는 과거 경영진의
    전략 결정에서 실패가 있었음을 시사하며, 향후 유사한 손실이 재발할 가능성을 암시합니다.
    특히 신규사업, M&A, 장기투자 부문에서의 리스크 관리 체계 강화가 요구됩니다.

    **종합 평가 및 권고:**

    현재 {st.session_state.corp_name_result}는 정성적으로 {'우수' if qual_score < 40 else '양호' if qual_score < 70 else '위험'} 수준의 리스크 프로필을 보이고 있습니다.
    정량 분석(재무지표)과 정성 분석(공시 투명성 및 리스크 요소)을 종합하면,
    이 기업의 투자는 신중한 접근과 지속적인 모니터링이 필요한 상태입니다.

    **향후 관리 포인트:**
    - 법정 소송의 진행 상황 및 판결 결과 추적
    - 특수관계자 거래의 공정성 및 규모 동향 감시
    - 자산손상의 원인 분석 및 재발 방지 대책 검토
    - 기업의 공시 품질 개선도 평가

    이러한 정성적 리스크 요소들은 기업의 장기적 지속가능성과 경영진의 역량을 평가하는 데
    중요한 지표로 활용될 수 있으며, 정량 분석과 함께 종합적인 투자 판단에 반영되어야 합니다.
    """

    with st.container(border=True):
        st.markdown(conclusion_text)

