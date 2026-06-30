# -*- coding: utf-8 -*-
"""
리스크 시나리오 분석 뷰
4가지 위기 시나리오에 따른 스트레스 테스트
"""

import streamlit as st
from utils.ui_helpers import show_section_header
from utils.financial_analysis import scenario_stress_test, find_account_value


def render_scenarios():
    """리스크 시나리오를 렌더링합니다."""

    # ========================================================================
    # 기본 정보
    # ========================================================================

    st.markdown(f"### {st.session_state.corp_name_result} 리스크 시나리오 분석")
    st.markdown("---")

    st.info("""
    💡 **스트레스 테스트란?**

    과거 위기 시나리오(금융위기, 팬데믹, 금리 상승 등)를 가정하여 기업이 얼마나 잘 견딜 수 있는지 검증하는 분석 방법입니다.
    재무 지표에 충격을 적용한 후 Z-Score 변화를 통해 회복력을 평가합니다.
    """)

    st.markdown("---")

    # ========================================================================
    # 재무 데이터 준비
    # ========================================================================

    financial_df = st.session_state.financial_df
    analysis = st.session_state.analysis

    financial_data = {
        "debt_ratio": analysis.get('debt_ratio', 100),
        "liquidity_ratio": analysis.get('current_ratio', 200),
    }

    if financial_df is not None:
        sales = find_account_value(financial_df, ['매출액', '매출', 'revenue'])
        ar = find_account_value(financial_df, ['매출채권', '기타채권'])
        if sales and ar:
            financial_data["ar_turnover"] = sales / ar if ar > 0 else 1

        ocf = find_account_value(financial_df, ['영업활동', '영업현금'])
        if ocf:
            financial_data["operating_cash_flow"] = ocf

    # ========================================================================
    # 시나리오 선택
    # ========================================================================

    show_section_header("🎯 시나리오 선택")

    col1, col2, col3, col4 = st.columns(4)

    selected_scenario = None

    with col1:
        if st.button("2008년 금융위기", use_container_width=True, key="crisis_2008"):
            selected_scenario = "crisis_2008"

    with col2:
        if st.button("COVID-19 팬데믹", use_container_width=True, key="covid19"):
            selected_scenario = "covid19"

    with col3:
        if st.button("금리 상승", use_container_width=True, key="rate_hike"):
            selected_scenario = "rate_hike"

    with col4:
        if st.button("산업 침체", use_container_width=True, key="industry_decline"):
            selected_scenario = "industry_decline"

    st.markdown("")

    # ========================================================================
    # 선택된 시나리오 결과
    # ========================================================================

    if selected_scenario:
        with st.spinner("스트레스 테스트 실행 중..."):
            result = scenario_stress_test(financial_data, selected_scenario)

        scenario_name = result.get('scenario_name', '')
        recommendation = result.get('recommendation', '')
        resilience = result.get('resilience', '')
        original_z = result.get('original_z_score', 0)
        shocked_z = result.get('shocked_z_score', 0)
        change_pct = result.get('change_percentage', 0)

        show_section_header(f"📊 {scenario_name} 분석 결과")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("기존 Z-Score", f"{original_z:.2f}")
            st.caption("정상 상태")

        with col2:
            st.metric("충격 후 Z-Score", f"{shocked_z:.2f}")
            st.caption(f"변화율: {change_pct:+.1f}%")

        with col3:
            if resilience == "견딜 수 있음":
                st.success(f"🟢 {resilience}")
            elif resilience == "위험":
                st.warning(f"🟠 {resilience}")
            else:
                st.error(f"🔴 {resilience}")
            st.caption("회복력 평가")

        st.markdown("---")

        st.markdown("**Z-Score 판정 기준:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🟢 견딜 수 있음")
            st.markdown("Z > 2.99\n\n기업은 충분한 회복력을 보유")

        with col2:
            st.markdown("#### 🟠 위험")
            st.markdown("1.81 < Z ≤ 2.99\n\n그레이존 - 주의 필요")

        with col3:
            st.markdown("#### 🔴 심각")
            st.markdown("Z ≤ 1.81\n\n심각한 위기 상황")

        st.markdown("---")

        st.markdown("**권고사항:**")

        with st.container(border=True):
            st.markdown(recommendation)

        st.markdown("---")

        with st.expander("📖 이 시나리오의 충격 요소"):
            shock_desc = {
                "crisis_2008": """
                **2008년 금융위기 특성:**
                - 부채비율 +30% (신용경색)
                - 유동비율 -30% (자금 경색)
                - 매출채권 회전율 -10%
                - 영업현금흐름 -20%
                - 순이익 -30%

                **영향:** 신용 시장 마비로 인한 자금 조달 어려움
                """,
                "covid19": """
                **COVID-19 팬데믹 특성:**
                - 부채비율 +10%
                - 유동비율 -15%
                - 매출채권 회전율 -10%
                - 영업현금흐름 -40% (매출 급감)
                - 순이익 -35%

                **영향:** 산업 특성에 따라 극심한 영업 타격
                """,
                "rate_hike": """
                **금리 상승 특성:**
                - 부채비율 +15% (이자 부담 증가)
                - 유동비율 -20%
                - 매출채권 회전율 -5%
                - 영업현금흐름 -10%
                - 순이익 -15%

                **영향:** 고금리로 인한 이자비용 증가
                """,
                "industry_decline": """
                **산업 침체 특성:**
                - 부채비율 +10%
                - 유동비율 -15%
                - 매출채권 회전율 -15% (수요 감소)
                - 영업현금흐름 -30%
                - 순이익 -25%

                **영향:** 산업 전반적 수요 감소 및 구조조정
                """
            }

            st.markdown(shock_desc.get(selected_scenario, ""))

    else:
        show_section_header("📋 모든 시나리오 개요")

        st.markdown("""
        | 시나리오 | 시기 | 특징 | 심각도 |
        |--------|------|------|--------|
        | 🔴 2008년 금융위기 | 금융 시장 | 신용 경색, 자금 조달 어려움 | 매우 높음 |
        | 🔴 COVID-19 팬데믹 | 팬데믹 | 산업별로 극심한 영업 충격 | 매우 높음 |
        | 🟠 금리 상승 | 통화정책 | 이자비용 증가로 수익성 악화 | 중간 |
        | 🟠 산업 침체 | 경기 | 산업 구조조정, 수요 감소 | 중간 |

        **각 시나리오를 클릭하여 상세 분석 결과를 확인하세요.**
        """)

        st.info("""
        💡 **해석 방법:**

        - 모든 시나리오에서 **"견딜 수 있음"** 평가가 나올수록 안전
        - Z-Score가 높을수록 회복력이 좋음
        - 여러 시나리오에서 위험이 나타나면 종합 리스크 관리 필요
        """)
