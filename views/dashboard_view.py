# -*- coding: utf-8 -*-
"""
종합 리스크 대시보드 뷰
최종 위험 등급, 정량vs정성 비교, 5년 추세 시각화
"""

import streamlit as st
import plotly.graph_objects as go
from utils.ui_helpers import show_section_header
from utils.qualitative_analysis import generate_final_report_paragraph


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

    with st.spinner("최종 판정 근거 분석 중..."):
        try:
            # LLM 객체 확인
            if "llm" not in st.session_state:
                raise ValueError("LLM 객체가 초기화되지 않았습니다.")

            # LLM으로 최종 판정 근거 문단 생성
            final_report = generate_final_report_paragraph(
                st.session_state.corp_name_result,
                final_risk,
                analysis,
                qualitative_risk,
                st.session_state.llm
            )

            # 깔끔한 보고서 스타일로 표시 (토글/개조식 없음)
            st.markdown(f"""
            <div style="background-color: #f8fafb; border-left: 4px solid #2d6a4f; padding: 20px; border-radius: 8px; margin: 20px 0; line-height: 1.8;">
                <p style="font-size: 1.05em; color: #1b4332; margin: 0; font-family: 'Noto Sans KR', sans-serif;">
                    {final_report}
                </p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"분석 중 오류: {str(e)}")
            st.markdown(f"""
            <div style="background-color: #f8fafb; border-left: 4px solid #2d6a4f; padding: 20px; border-radius: 8px; margin: 20px 0; line-height: 1.8;">
                <p style="font-size: 1.05em; color: #1b4332; margin: 0;">
                    {st.session_state.corp_name_result}은(는) 정량적으로 {analysis['financial_risk_score']:.1f}/100의 위험도를 보이며,
                    정성적으로는 {qualitative_risk['qualitative_risk_score']:.1f}/100의 리스크가 확인되었습니다.
                    이를 통합하여 최종 {final_risk['grade_label']} 등급으로 판정되었습니다.
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ========================================================================
    # 세부 분석 지표 (바로 보여주기)
    # ========================================================================

    show_section_header("🔍 세부 분석 지표")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background-color: #f8fafb; border-left: 4px solid #4a90a4; padding: 16px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: #1b4332; margin-top: 0;">📊 정량 분석</h4>
            <p style="color: #555;"><strong>종합 위험도:</strong> {analysis['financial_risk_score']:.1f}/100</p>
            <p style="color: #555; margin: 8px 0;"><strong>세부 지표:</strong></p>
            <ul style="color: #555; margin: 5px 0;">
                <li>매출채권 회전율: {analysis['component_scores']['revenue_quality']:.0f}/100</li>
                <li>유동비율: {analysis['component_scores']['liquidity_stress']:.0f}/100</li>
                <li>부채비율: {analysis['component_scores']['leverage_risk']:.0f}/100</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color: #f8fafb; border-left: 4px solid #a46c4a; padding: 16px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: #1b4332; margin-top: 0;">📋 정성 분석</h4>
            <p style="color: #555;"><strong>종합 위험도:</strong> {qualitative_risk['qualitative_risk_score']:.1f}/100</p>
            <p style="color: #555; margin: 8px 0;"><strong>발견 내역:</strong></p>
            <ul style="color: #555; margin: 5px 0;">
                <li>우발채무/소송: {qualitative_risk['risk_breakdown'].get('contingent_liabilities', 0)}건</li>
                <li>특수거래: {qualitative_risk['risk_breakdown'].get('related_party_transactions', 0)}건</li>
                <li>자산손상: {qualitative_risk['risk_breakdown'].get('asset_impairment', 0)}건</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
