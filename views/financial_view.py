# -*- coding: utf-8 -*-
"""
정량 재무 분석 뷰
매출채권 회전율, 유동비율, 부채비율, ROE, ROA 등 정량 지표 분석
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
    # 핵심 지표 (4열 일렬 배치 + 만점 기준 명시 + 상태 평가)
    # ========================================================================

    show_section_header("📊 핵심 지표")

    col1, col2, col3, col4 = st.columns(4)

    component_scores = analysis.get('component_scores', {})
    overall_risk_status = analysis.get('overall_risk_status', {})
    revenue_quality_status = analysis.get('revenue_quality_status', {})
    liquidity_stress_status = analysis.get('liquidity_stress_status', {})
    leverage_risk_status = analysis.get('leverage_risk_status', {})

    with col1:
        with st.container(border=True):
            st.metric("종합 위험도", f"{analysis['financial_risk_score']:.1f}/100")
            status_emoji = overall_risk_status.get('emoji', '❓')
            status_text = overall_risk_status.get('status_ko', '평가 불가')
            st.caption(f"{status_emoji} {status_text}")

    with col2:
        with st.container(border=True):
            st.metric("매출 질", f"{component_scores['revenue_quality']:.0f}/100")
            status_emoji = revenue_quality_status.get('emoji', '❓')
            status_text = revenue_quality_status.get('status_ko', '평가 불가')
            st.caption(f"{status_emoji} {status_text}")

    with col3:
        with st.container(border=True):
            st.metric("유동성", f"{component_scores['liquidity_stress']:.0f}/100")
            status_emoji = liquidity_stress_status.get('emoji', '❓')
            status_text = liquidity_stress_status.get('status_ko', '평가 불가')
            st.caption(f"{status_emoji} {status_text}")

    with col4:
        with st.container(border=True):
            st.metric("부채", f"{component_scores['leverage_risk']:.0f}/100")
            status_emoji = leverage_risk_status.get('emoji', '❓')
            status_text = leverage_risk_status.get('status_ko', '평가 불가')
            st.caption(f"{status_emoji} {status_text}")

    st.markdown("")

    # ========================================================================
    # 수익성 지표 (ROE, ROA)
    # ========================================================================

    col5, col6 = st.columns(2)

    roe = analysis.get('roe')
    roa = analysis.get('roa')

    with col5:
        with st.container(border=True):
            if roe is not None:
                st.metric("ROE", f"{roe:.2f}%", delta="자기자본이익률")
                if roe > 15:
                    st.caption("✅ 우수한 수익성")
                elif roe > 10:
                    st.caption("🟡 양호한 수익성")
                else:
                    st.caption("⚠️ 개선 필요")
            else:
                st.metric("ROE", "데이터 없음")

    with col6:
        with st.container(border=True):
            if roa is not None:
                st.metric("ROA", f"{roa:.2f}%", delta="총자산이익률")
                if roa > 8:
                    st.caption("✅ 우수한 자산 활용")
                elif roa > 5:
                    st.caption("🟡 양호한 자산 활용")
                else:
                    st.caption("⚠️ 개선 필요")
            else:
                st.metric("ROA", "데이터 없음")

    st.markdown("")
    st.markdown("---")

    # ========================================================================
    # 정량 평가 분석 (통합 탭 구조)
    # ========================================================================

    show_section_header("📈 정량 평가 분석")

    tab_framework, tab_revenue, tab_liquidity, tab_leverage, tab_profitability = st.tabs([
        "📋 분석 체계",
        "📈 매출 질",
        "💧 유동성",
        "🛡️ 부채",
        "💰 수익성"
    ])

    # ========================================================================
    # 탭 1: 분석 체계
    # ========================================================================

    with tab_framework:
        st.markdown("""
        ### 📊 정량 재무 분석 체계

        본 분석 시스템은 기업의 **재무 건전성**을 정량적으로 평가하기 위해 다음과 같은 통합 평가 구조를 적용합니다.

        **가중치 배분:**
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 매출 질", "40%", "수익 창출")
        with col2:
            st.metric("💧 유동성", "35%", "단기 안정성")
        with col3:
            st.metric("🛡️ 부채", "25%", "장기 안정성")

        st.markdown("""
        **통합 점수 산출식:**
        ```
        종합 위험도 = (매출질 × 40%) + (유동성 × 35%) + (부채 × 25%)
        ```

        **평가 기준:**
        - 🟢 **[우수]** (0~40점): 재무 건전 상태
        - 🟡 **[양호]** (40~70점): 주의 필요
        - 🔴 **[위험]** (70~100점): 개선 시급

        각 지표별로 3단계 상태([정상/주의/경고])로 세분화된 평가를 수행하며,
        계산된 실제 지표값과 함께 전문 애널리스트 관점의 정성적 평가를 병행합니다.
        """)

    # ========================================================================
    # 탭 2: 매출 질
    # ========================================================================

    with tab_revenue:
        st.markdown("### 📈 매출 질 평가")

        # 1단계: 판정 상태 최우선 노출
        revenue_score = component_scores.get('revenue_quality', 0)
        status = revenue_quality_status.get('status_ko', '평가 불가')
        emoji = revenue_quality_status.get('emoji', '❓')

        with st.container(border=True):
            st.markdown(f"""
            #### {emoji} 평가 상태: **{status}**

            **지표 점수:** {revenue_score:.0f}/100

            **의미:** 기업의 현금 창출 능력이 {'우수' if revenue_score < 30 else '주의 필요' if revenue_score < 60 else '개선 요망'}한 수준입니다.
            """)

        st.markdown("---")

        # 2단계: 구체적인 평가 결과 서술
        st.markdown("#### 📋 분석 평가")

        analysis_text = f"""
        매출채권 회전율과 영업현금흐름을 기반으로 {st.session_state.corp_name_result}의 매출 질을 평가합니다.

        매출채권 회전율이 높을수록 외상 회수가 빠르고 현금흐름이 건강합니다. 동시에 영업활동에서 발생하는 실제 현금흐름이 충분한지 검증함으로써,
        순수한 수익성을 파악할 수 있습니다. 현재 매출 점수 **{revenue_score:.0f}/100**은 기업의 현금 창출 능력이
        {'양호' if revenue_score < 30 else '주의 필요' if revenue_score < 60 else '개선 요망'}한 수준임을 의미합니다.
        """

        st.markdown(analysis_text)

        if detailed:
            with st.container(border=True):
                for key, value in detailed.items():
                    if 'ar' in key.lower() or 'ocf' in key.lower() or 'revenue' in key.lower():
                        st.caption(f"📌 {value}")

        st.markdown("---")

        # 3단계: 평가 기준 설명
        st.markdown("#### 📖 평가 기준 및 정의")

        st.markdown("""
        **매출채권 회전율**
        - 정의: 매출액 ÷ 평균 매출채권
        - 의미: 외상매출이 1년간 몇 번 회수되는지 나타냄
        - 기준:
          - ≥4배: 정상 (회수 빠름)
          - 2~4배: 보통
          - <2배: 주의 (회수 지연)

        **영업현금흐름**
        - 정의: 영업활동으로 인한 실제 현금 유입
        - 의미: 매출액의 실제 현금화 정도
        - 판단:
          - 양수 & 충분: 신뢰성 높음
          - 음수: 현금 악화 신호
        """)

    # ========================================================================
    # 탭 3: 유동성
    # ========================================================================

    with tab_liquidity:
        st.markdown("### 💧 유동성 평가")

        # 1단계: 판정 상태 최우선 노출
        current_ratio_val = analysis.get('current_ratio')
        current_ratio_status = analysis.get('current_ratio_status', {})
        status = current_ratio_status.get('status_ko', '평가 불가')
        emoji = current_ratio_status.get('emoji', '❓')
        liquidity_score = component_scores.get('liquidity_stress', 0)

        with st.container(border=True):
            st.markdown(f"""
            #### {emoji} 평가 상태: **{status}**

            **유동비율:** {current_ratio_val:.1f}% (기준: 150% 이상 정상)

            **지표 점수:** {liquidity_score:.0f}/100
            """)

        st.markdown("---")

        # 2단계: 구체적인 평가 결과 서술
        st.markdown("#### 📋 분석 평가")

        if current_ratio_val:
            liquidity_text = f"""
            **유동비율**(유동자산 ÷ 유동부채 × 100)은 기업의 단기 상환능력을 나타내는 핵심 지표입니다.

            {st.session_state.corp_name_result}의 유동비율은 **{current_ratio_val:.1f}%**로, 판정 기준에 따라 **{emoji} [{status}]** 상태로 평가됩니다.
            """

            if status == "정상":
                liquidity_text += f"""이는 단기 채무를 충분히 충당할 수 있는 유동자산이 확보되어 있어 재무 안정성이 양호하다는 의미입니다."""
            elif status == "주의":
                liquidity_text += f"""유동자산과 유동부채의 균형이 맞는 수준이지만, 추가 유동자산 확보 또는 단기 부채 감축을 통해 개선의 여지가 있습니다."""
            else:  # 경고
                liquidity_text += f"""유동부채가 유동자산을 초과하는 상태입니다. 단기 유동성이 긴급한 수준이므로 즉시 재정 건전성 개선이 필요합니다."""

            st.markdown(liquidity_text)
        else:
            st.info("유동비율 데이터를 사용할 수 없습니다.")

        if detailed:
            with st.container(border=True):
                for key, value in detailed.items():
                    if 'liquidity' in key.lower():
                        st.caption(f"📌 {value}")

        st.markdown("---")

        # 3단계: 평가 기준 설명
        st.markdown("#### 📖 평가 기준 및 정의")

        st.markdown("""
        **유동비율 (Current Ratio)**
        - 계산식: 유동자산 ÷ 유동부채 × 100
        - 의미: 1년 내 상환할 부채를 커버할 수 있는 자산 비율

        **판정 기준:**
        | 상태 | 범위 | 해석 |
        |------|------|------|
        | 🟢 정상 | ≥150% | 단기 채무 충당 능력 양호 |
        | 🟡 주의 | 100~150% | 유동성 개선 필요 |
        | 🔴 경고 | <100% | 단기 부채 초과 (긴급) |

        **학술 기준:**
        - 150% 이상: 안정적 유동성 확보
        - 100% 미만: 재정위기 신호
        """)

    # ========================================================================
    # 탭 4: 부채
    # ========================================================================

    with tab_leverage:
        st.markdown("### 🛡️ 부채 평가")

        # 1단계: 판정 상태 최우선 노출
        debt_ratio_val = analysis.get('debt_ratio')
        debt_ratio_status = analysis.get('debt_ratio_status', {})
        status = debt_ratio_status.get('status_ko', '평가 불가')
        emoji = debt_ratio_status.get('emoji', '❓')
        leverage_score = component_scores.get('leverage_risk', 0)

        with st.container(border=True):
            st.markdown(f"""
            #### {emoji} 평가 상태: **{status}**

            **부채비율:** {debt_ratio_val:.1f}% (기준: 100% 이하 정상)

            **지표 점수:** {leverage_score:.0f}/100
            """)

        st.markdown("---")

        # 2단계: 구체적인 평가 결과 서술
        st.markdown("#### 📋 분석 평가")

        if debt_ratio_val:
            debt_text = f"""
            **부채비율**(부채 ÷ 자본 × 100)은 기업의 재무 레버리지 수준과 장기 안정성을 보여주는 지표입니다.

            {st.session_state.corp_name_result}의 부채비율은 **{debt_ratio_val:.1f}%**로, 판정 기준에 따라 **{emoji} [{status}]** 상태로 평가됩니다.
            """

            if status == "정상":
                debt_text += f"""부채 수준이 적절하게 관리되고 있어 재무 안정성과 지속 가능성이 양호합니다."""
            elif status == "주의":
                debt_text += f"""중간 수준의 부채 부담을 안고 있습니다. 부채 수준이 상승 추세이거나 자본 대비 부채가 높은 편이므로, 향후 부채 감축과 자본 확충을 통한 개선이 권장됩니다."""
            else:  # 경고
                debt_text += f"""부채가 자본을 크게 초과하는 고위험 상태입니다. 부채 규모가 과도하여 재무 구조 개선이 시급합니다. 자본금 확충 또는 부채 감축을 통한 재정 건전화가 필요합니다."""

            st.markdown(debt_text)
        else:
            st.info("부채비율 데이터를 사용할 수 없습니다.")

        if detailed:
            with st.container(border=True):
                for key, value in detailed.items():
                    if 'leverage' in key.lower():
                        st.caption(f"📌 {value}")

        st.markdown("---")

        # 3단계: 평가 기준 설명
        st.markdown("#### 📖 평가 기준 및 정의")

        st.markdown("""
        **부채비율 (Debt-to-Equity Ratio)**
        - 계산식: 부채총계 ÷ 자본총계 × 100
        - 의미: 자본금 대비 부채 비중

        **판정 기준:**
        | 상태 | 범위 | 해석 |
        |------|------|------|
        | 🟢 정상 | ≤100% | 자본과 부채의 균형 양호 |
        | 🟡 주의 | 100~200% | 부채 비중 상승 (주의) |
        | 🔴 경고 | >200% | 부채가 자본의 2배 초과 |

        **학술 기준:**
        - 100% 이하: 자본 중심 재무구조 (안정적)
        - 200% 이상: 고부채 구조 (위험)
        """)

    # ========================================================================
    # 탭 5: 수익성
    # ========================================================================

    with tab_profitability:
        st.markdown("### 💰 수익성 지표 평가")

        # 1단계: ROE/ROA 현황
        st.markdown("#### 📊 수익성 지표 현황")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("**ROE (자기자본이익률)**")
                if roe is not None:
                    st.metric("", f"{roe:.2f}%")
                    if roe > 15:
                        st.caption("✅ 우수")
                    elif roe > 10:
                        st.caption("🟡 양호")
                    else:
                        st.caption("⚠️ 개선필요")
                else:
                    st.metric("", "데이터 없음")

        with col2:
            with st.container(border=True):
                st.markdown("**ROA (총자산이익률)**")
                if roa is not None:
                    st.metric("", f"{roa:.2f}%")
                    if roa > 8:
                        st.caption("✅ 우수")
                    elif roa > 5:
                        st.caption("🟡 양호")
                    else:
                        st.caption("⚠️ 개선필요")
                else:
                    st.metric("", "데이터 없음")

        st.markdown("---")

        # 2단계: 분석 평가
        st.markdown("#### 📋 분석 평가")

        roe_desc = ""
        if roe:
            if roe > 15:
                roe_desc = "자본을 매우 효율적으로 활용하여 우수한 수익성을 달성"
            elif roe > 10:
                roe_desc = "자본을 효율적으로 활용하고 있으며 양호한 수익성 수준"
            else:
                roe_desc = "자본 활용 효율이 낮아 개선이 필요한 상태"

        roa_desc = ""
        if roa:
            if roa > 8:
                roa_desc = "자산을 매우 효율적으로 운영하여 높은 이익 창출"
            elif roa > 5:
                roa_desc = "자산을 효율적으로 운영하고 있으며 양호한 수준"
            else:
                roa_desc = "자산 활용 효율이 낮아 개선이 필요한 상태"

        st.markdown(f"""
        {st.session_state.corp_name_result}의 수익성을 평가하면 다음과 같습니다.

        **ROE 평가:** {roe_desc if roe else '데이터 없음'}

        **ROA 평가:** {roa_desc if roa else '데이터 없음'}

        두 지표를 비교하면, ROE와 ROA의 차이는 기업이 부채를 활용한 레버리지 효과를 나타냅니다.
        일반적으로 ROE > ROA인 경우 부채를 활용하여 자본 수익률을 높이는 것으로 평가됩니다.
        """)

        st.markdown("---")

        # 3단계: 평가 기준 설명
        st.markdown("#### 📖 평가 기준 및 정의")

        st.markdown("""
        **ROE (자기자본이익률 = Return on Equity)**
        - 계산식: 당기순이익 ÷ 자본총계 × 100
        - 의미: 자본금으로 얼마나 이익을 창출했는가?

        **판정 기준:**
        | 평가 | 범위 | 해석 |
        |------|------|------|
        | ✅ 우수 | >15% | 매우 효율적인 자본 활용 |
        | 🟡 양호 | 10~15% | 양호한 수익성 |
        | ⚠️ 개선필요 | <10% | 자본 활용 효율 낮음 |

        ---

        **ROA (총자산이익률 = Return on Assets)**
        - 계산식: 당기순이익 ÷ 자산총계 × 100
        - 의미: 자산으로 얼마나 이익을 창출했는가?

        **판정 기준:**
        | 평가 | 범위 | 해석 |
        |------|------|------|
        | ✅ 우수 | >8% | 효율적인 자산 활용 |
        | 🟡 양호 | 5~8% | 양호한 자산 운영 |
        | ⚠️ 개선필요 | <5% | 자산 활용 효율 낮음 |

        ---

        **ROE vs ROA 분석팁:**
        - **ROE > ROA (긍정):** 부채를 활용하여 자본 수익률을 높임
        - **ROE < ROA (주의):** 부채가 이익 창출에 부담
        - **둘 다 낮음:** 원가 관리 또는 경영 효율 개선 필요
        """)
