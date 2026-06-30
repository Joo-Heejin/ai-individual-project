# -*- coding: utf-8 -*-
"""
종합 리스크 대시보드 뷰
최종 위험 등급, 정량vs정성 비교, 5년 추세 시각화
"""

import streamlit as st
import plotly.graph_objects as go
from utils.ui_helpers import show_section_header


def render_dashboard():
    """종합 리스크 대시보드를 렌더링합니다."""

    # ========================================================================
    # 기본 정보
    # ========================================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("기업명", st.session_state.corp_name_result)
    with col2:
        st.metric("기업코드", st.session_state.corp_code)
    with col3:
        st.metric("보고서", st.session_state.report_type)
    with col4:
        st.metric("공시일", st.session_state.report_date)

    st.markdown("---")

    # ========================================================================
    # 최종 위험 등급 (강조)
    # ========================================================================

    show_section_header("🎯 최종 위험 등급")

    final_risk = st.session_state.final_risk
    final_score = final_risk['final_integrated_score']
    final_grade = final_risk['final_risk_grade']
    color = final_risk['color']
    grade_label = final_risk['grade_label']

    color_map = {
        "red": "#c41c3b",
        "orange": "#f57c00",
        "green": "#2e7d32"
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
                <p style="font-size: 2.5em; font-weight: 700; margin: 10px 0 0 0; color: {color_map[color]};">{grade_label}</p>
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

    # ========================================================================
    # 정량 vs 정성 비교
    # ========================================================================

    show_section_header("📊 정량 vs 정성 위험도 비교")

    col_quant, col_qual = st.columns(2)

    with col_quant:
        with st.container(border=True):
            st.markdown("### 📈 정량 위험도 (재무 지표)")
            analysis = st.session_state.analysis
            quant_score = analysis['financial_risk_score']
            st.metric("종합 점수", f"{quant_score:.1f}/100", delta="가중치 60%")
            st.caption(f"평가: {analysis['risk_level']}")

            revenue = analysis['component_scores']['revenue_quality']
            liquidity = analysis['component_scores']['liquidity_stress']
            leverage = analysis['component_scores']['leverage_risk']

            st.markdown(f"""
            **지표별 점수:**
            - 매출 질: {revenue:.0f}/100
            - 유동성: {liquidity:.0f}/100
            - 부채: {leverage:.0f}/100
            """)

    with col_qual:
        with st.container(border=True):
            st.markdown("### 📋 정성 위험도 (주석 분석)")
            qualitative_risk = st.session_state.qualitative_risk
            qual_score = qualitative_risk['qualitative_risk_score']
            st.metric("종합 점수", f"{qual_score:.1f}/100", delta="가중치 40%")
            st.caption(f"발견된 카테고리: {qualitative_risk['risk_count']}개")

            breakdown = qualitative_risk['risk_breakdown']
            st.markdown(f"""
            **카테고리별 발견:**
            - 우발채무: {breakdown.get('contingent_liabilities', 0)}개
            - 특수거래: {breakdown.get('related_party_transactions', 0)}개
            - 자산손상: {breakdown.get('asset_impairment', 0)}개
            """)

    st.markdown("---")

    # ========================================================================
    # 5년 위험도 추세
    # ========================================================================

    show_section_header("📈 5년 위험도 추세")

    trend_scores = st.session_state.get("trend_scores")

    if trend_scores and trend_scores.get("status") != "오류":
        years = [2020, 2021, 2022, 2023, 2024]
        scores = []
        valid_years = []

        for year in years:
            score = trend_scores.get(year)
            if score is not None:
                scores.append(score)
                valid_years.append(year)

        if len(valid_years) > 0:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=valid_years,
                y=scores,
                mode='lines+markers',
                name='위험도 추세',
                line=dict(color='#2d6a4f', width=3),
                marker=dict(size=10, color='#2d6a4f'),
                hovertemplate='<b>%{x}년</b><br>위험도: %{y:.1f}/100<extra></extra>'
            ))

            if 2024 in valid_years:
                idx = valid_years.index(2024)
                fig.add_trace(go.Scatter(
                    x=[2024],
                    y=[scores[idx]],
                    mode='markers+text',
                    name='최신 (2024)',
                    marker=dict(size=16, color='#c41c3b', symbol='star',
                               line=dict(color='#1b4332', width=2)),
                    text=['최신'],
                    textposition='top center',
                    textfont=dict(color='#c41c3b', size=12),
                    hovertemplate='<b>2024 (최신)</b><br>위험도: %{y:.1f}/100<extra></extra>'
                ))

            fig.update_layout(
                title='',
                xaxis_title='연도',
                yaxis_title='위험도 점수 (0-100)',
                hovermode='x unified',
                template='plotly_white',
                height=400,
                showlegend=True,
                legend=dict(x=0.02, y=0.98),
                yaxis=dict(range=[0, 100]),
                xaxis=dict(tickmode='linear', tick0=2020, dtick=1),
                margin=dict(l=60, r=60, t=20, b=60),
                font=dict(family="Pretendard, sans-serif")
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("**연도별 상세 데이터:**")
            trend_table = []
            for year in valid_years:
                score = trend_scores.get(year)
                trend_table.append({"연도": year, "위험도": f"{score:.1f}/100"})

            st.dataframe(trend_table, use_container_width=True, hide_index=True)

            st.markdown("**추세 분석:**")
            if len(scores) > 1:
                latest = scores[-1]
                earliest = scores[0]
                change = latest - earliest

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("최초 (2020)", f"{earliest:.1f}")
                with col2:
                    st.metric("최근 (2024)", f"{latest:.1f}")
                with col3:
                    st.metric("변화", f"{change:+.1f}", delta_color="inverse")

            st.info(f"✅ **DART 공시 기반 실제 데이터**\n\n5년간의 재무 위험도 추세를 통해 기업의 장기 재무 건전성 추이를 확인할 수 있습니다.")

        else:
            st.warning("표시할 유효한 데이터가 없습니다.")
    else:
        st.warning("⚠️ 5년 데이터 조회 실패 - 현재 연도 데이터만 사용 중입니다.")

    st.markdown("---")

    # ========================================================================
    # 최종 판정 근거
    # ========================================================================

    show_section_header("📋 최종 판정 근거")

    with st.expander("정량 분석 상세 내용", expanded=False):
        st.markdown(f"""
        **정량 분석 구성:**
        - 매출채권 회전율 (40% 가중치)
        - 유동비율 (35% 가중치)
        - 부채비율 (25% 가중치)

        **판정 기준:**
        - 위험도 > 70: 고위험
        - 50 < 위험도 ≤ 70: 중위험
        - 위험도 ≤ 50: 저위험
        """)

        if analysis.get('detailed_findings'):
            st.markdown("**세부 분석 결과:**")
            for key, value in analysis['detailed_findings'].items():
                st.caption(f"• {value}")

    with st.expander("정성 분석 상세 내용", expanded=False):
        scoring_details = qualitative_risk.get('scoring_details', {})
        rationale = scoring_details.get('rationale', '')

        if rationale:
            st.markdown(rationale)
