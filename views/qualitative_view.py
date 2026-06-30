# -*- coding: utf-8 -*-
"""
정성적 크로스체킹 뷰
Claude LLM 기반 경영진 설명 및 이해관계자 리스크 검증
"""

import streamlit as st
from utils.ui_helpers import show_section_header


def render_qualitative():
    """정성적 크로스체킹을 렌더링합니다."""

    # ========================================================================
    # 기본 정보
    # ========================================================================

    st.markdown(f"### {st.session_state.corp_name_result} 정성적 리스크 검증")
    st.markdown("---")

    # ========================================================================
    # 정성 위험도 스코어
    # ========================================================================

    show_section_header("📊 정성 위험도 종합")

    qualitative_risk = st.session_state.qualitative_risk
    qual_score = qualitative_risk['qualitative_risk_score']
    breakdown = qualitative_risk['risk_breakdown']

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        with st.container(border=True):
            st.metric("종합 점수", f"{qual_score:.1f}")
            st.caption("리스크 카테고리")

    with col2:
        with st.container(border=True):
            contingent = breakdown.get('contingent_liabilities', 0)
            st.metric("우발채무", f"{contingent}개")
            st.caption("소송/법적")

    with col3:
        with st.container(border=True):
            related = breakdown.get('related_party_transactions', 0)
            st.metric("특수거래", f"{related}개")
            st.caption("관계자 거래")

    with col4:
        with st.container(border=True):
            asset = breakdown.get('asset_impairment', 0)
            st.metric("자산손상", f"{asset}개")
            st.caption("M&A/손실")

    with col5:
        with st.container(border=True):
            assessment = breakdown.get('investment_assessment', 0)
            st.metric("최종평가", "포함" if assessment else "미포함")
            st.caption("투자평가")

    st.markdown("")

    # ========================================================================
    # 상세 점수 정당성
    # ========================================================================

    show_section_header("📋 점수 계산 근거")

    scoring_details = qualitative_risk.get('scoring_details', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        contingent_score = scoring_details.get('contingent_score', 0)
        st.metric("우발채무 점수", f"{contingent_score:.1f}/45")

    with col2:
        related_score = scoring_details.get('related_score', 0)
        st.metric("특수거래 점수", f"{related_score:.1f}/40")

    with col3:
        asset_score = scoring_details.get('asset_score', 0)
        st.metric("자산손상 점수", f"{asset_score:.1f}/40")

    with col4:
        assessment_score = scoring_details.get('assessment_score', 0)
        st.metric("평가 점수", f"{assessment_score:.0f}/25")

    st.markdown(f"""
    **점수 계산식:**
    ```
    {contingent_score:.1f} + {related_score:.1f} + {asset_score:.1f} + {assessment_score:.0f} = {qual_score:.1f}/100
    ```
    """)

    st.markdown("---")

    # ========================================================================
    # 상세 정당성 설명
    # ========================================================================

    show_section_header("🔍 점수 정당성 상세")

    rationale = scoring_details.get('rationale', '')

    if rationale:
        st.markdown(rationale)
    else:
        st.info("상세 분석 내용이 없습니다.")

    st.markdown("---")

    # ========================================================================
    # Claude 분석 텍스트
    # ========================================================================

    show_section_header("💬 Claude AI 분석 결과")

    tab1, tab2 = st.tabs(["경영진 관점 설명", "이해관계자 검증"])

    with tab1:
        st.markdown("### 📝 경영진의 재무 설명 (CFO 관점)")

        mgmt_response = st.session_state.get('mgmt_response', '')

        if mgmt_response:
            with st.container(border=True):
                st.markdown(mgmt_response)
        else:
            st.info("경영진 설명이 없습니다.")

    with tab2:
        st.markdown("### ⚖️ 이해관계자의 정밀 검증 (감시 변호사 관점)")

        caveats = st.session_state.get('caveats', '')

        if caveats:
            with st.container(border=True):
                st.markdown(caveats)
        else:
            st.info("이해관계자 검증이 없습니다.")

    st.markdown("---")

    # ========================================================================
    # 리스크 카테고리 상세
    # ========================================================================

    show_section_header("🎯 리스크 카테고리별 발견")

    risk_categories = st.session_state.get('risk_categories', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander("우발채무 & 소송", expanded=False):
            contingent_details = risk_categories.get('contingent_liabilities_details', [])
            if contingent_details:
                for detail in contingent_details:
                    st.markdown(f"• {detail}")
            else:
                st.caption("발견된 항목 없음")

    with col2:
        with st.expander("특수관계자 거래", expanded=False):
            related_details = risk_categories.get('related_party_transactions_details', [])
            if related_details:
                for detail in related_details:
                    st.markdown(f"• {detail}")
            else:
                st.caption("발견된 항목 없음")

    with col3:
        with st.expander("자산손상 & 투자손실", expanded=False):
            asset_details = risk_categories.get('asset_impairment_details', [])
            if asset_details:
                for detail in asset_details:
                    st.markdown(f"• {detail}")
            else:
                st.caption("발견된 항목 없음")

    st.markdown("---")

    # ========================================================================
    # 분석 방법론
    # ========================================================================

    with st.expander("📖 정성 분석 방법론"):
        st.markdown("""
        ### 정성 분석 구성

        **① 경영진 관점 (CFO 설명)**
        - 국제회계기준(IFRS) 준수 입증
        - 전략적 자산 취득 정당화
        - 리스크 관리 현황 설명

        **② 이해관계자 관점 (감시 변호사)**
        - 우발채무 및 소송 사건 추적
        - 특수관계자 거래 투명성 검증
        - 자산손상/투자손실 규모 분석

        **③ 점수 계산**
        - 우발채무: 항목당 15점 (최대 45점)
        - 특수관계자: 항목당 20점 (최대 40점)
        - 자산손상: 항목당 20점 (최대 40점)
        - 투자평가: 25점 (있으면 추가)
        - **총 최대 100점**
        """)
