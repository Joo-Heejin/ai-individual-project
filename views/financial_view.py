# -*- coding: utf-8 -*-
"""
정량 재무 분석 뷰
매출채권 회전율, 유동비율, 부채비율, 현금흐름 등 정량 지표 분석
"""

import streamlit as st
from utils.ui_helpers import show_section_header


def render_financials():
    """정량 재무 분석을 렌더링합니다."""

    analysis = st.session_state.analysis
    detailed = analysis.get('detailed_findings', {})

    # ========================================================================
    # 기본 정보
    # ========================================================================

    st.markdown(f"### {st.session_state.corp_name_result} 정량 재무 분석")
    st.markdown("---")

    # ========================================================================
    # 종합 위험도 스코어
    # ========================================================================

    show_section_header("📊 종합 위험도")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric("종합 위험도", f"{analysis['financial_risk_score']:.1f}/100")
            st.caption(f"평가: {analysis['risk_level']}")

    with col2:
        with st.container(border=True):
            component_scores = analysis['component_scores']
            st.metric("매출 질", f"{component_scores['revenue_quality']:.0f}/100")

    with col3:
        with st.container(border=True):
            st.metric("유동성", f"{component_scores['liquidity_stress']:.0f}/100")

    col4, col5 = st.columns(2)

    with col4:
        with st.container(border=True):
            st.metric("부채", f"{component_scores['leverage_risk']:.0f}/100")

    st.markdown("")

    # ========================================================================
    # 지표 상세 분석
    # ========================================================================

    show_section_header("🔍 지표별 상세 분석")

    tab1, tab2, tab3 = st.tabs(["매출 질", "유동성", "부채"])

    with tab1:
        st.markdown("### 📈 매출 질 평가")

        st.markdown("""
        **분석 항목:**
        - 매출채권 회전율: 매출 대비 매출채권 규모
        - 영업현금흐름: 실제 현금 유입 규모

        **판정 기준:**
        - 회전율 < 2배: 고위험 (70점)
        - 2배 ≤ 회전율 < 4배: 주의 (50점)
        - 회전율 ≥ 4배: 정상 (20점)
        - 영업현금 < 0: 고위험 (85점)
        """)

        with st.container(border=True):
            for key, value in detailed.items():
                if 'ar' in key.lower() or 'ocf' in key.lower():
                    icon = "⚠️" if "warning" in key.lower() else "✅"
                    st.markdown(f"{icon} {value}")

    with tab2:
        st.markdown("### 💰 유동성 평가")

        st.markdown("""
        **분석 항목:**
        - 유동비율: 유동자산 / 유동부채 × 100

        **판정 기준:**
        - 유동비율 < 100%: 고위험 (90점)
        - 100% ≤ 유동비율 < 150%: 주의 (60점)
        - 유동비율 ≥ 150%: 정상 (20점)
        """)

        if analysis.get('current_ratio'):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("유동비율", f"{analysis['current_ratio']:.1f}%")
            with col2:
                ratio_val = analysis['current_ratio']
                if ratio_val < 100:
                    st.error(f"⚠️ 단기 유동성 압박 상태")
                elif ratio_val < 150:
                    st.warning(f"⚠️ 주의 필요")
                else:
                    st.success(f"✅ 정상 수준")

        with st.container(border=True):
            for key, value in detailed.items():
                if 'liquidity' in key.lower():
                    icon = "⚠️" if "risk" in key.lower() else "✅"
                    st.markdown(f"{icon} {value}")

    with tab3:
        st.markdown("### 📉 부채 평가")

        st.markdown("""
        **분석 항목:**
        - 부채비율: 부채 / 자본 × 100

        **판정 기준:**
        - 부채비율 > 200%: 고위험 (80점)
        - 160% < 부채비율 ≤ 200%: 주의 (50점)
        - 부채비율 ≤ 160%: 정상 (20점)
        """)

        if analysis.get('debt_ratio'):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("부채비율", f"{analysis['debt_ratio']:.1f}%")
            with col2:
                debt_val = analysis['debt_ratio']
                if debt_val > 200:
                    st.error(f"🚨 부채 과다 상태")
                elif debt_val > 160:
                    st.warning(f"⚠️ 주의 필요")
                else:
                    st.success(f"✅ 정상 수준")

        with st.container(border=True):
            for key, value in detailed.items():
                if 'leverage' in key.lower():
                    icon = "⚠️" if "high" in key.lower() else "✅"
                    st.markdown(f"{icon} {value}")

    st.markdown("---")

    # ========================================================================
    # 모든 세부 분석
    # ========================================================================

    show_section_header("📋 모든 분석 항목")

    with st.expander("전체 분석 결과", expanded=False):
        st.markdown("**발견된 모든 지표:**")

        if detailed:
            for key, value in detailed.items():
                st.caption(f"✓ {value}")
        else:
            st.info("특이사항 없음")
