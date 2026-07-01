# -*- coding: utf-8 -*-
"""
소비재 산업 특화 리스크 시나리오 분석 뷰
CDIA 프레임워크 기반 고도화된 보고서 생성
"""

import streamlit as st
from utils.ui_helpers import show_section_header
from utils.financial_analysis import scenario_stress_test, find_account_value


def render_scenarios():
    """소비재 산업 특화 리스크 시나리오를 렌더링합니다."""

    # ========================================================================
    # CSS 스타일 정의 (전체 일관성 제어)
    # ========================================================================
    st.markdown("""
    <style>
    .scenario-narrative {
        font-size: 15px;
        line-height: 1.6;
        color: #333;
        padding: 20px;
        background-color: #f8fdf9;
        border-left: 4px solid #1f8e72;
        border-radius: 4px;
        margin: 15px 0;
    }
    .scenario-detail-box {
        font-size: 15px;
        line-height: 1.6;
        color: #333;
        padding: 20px;
        background-color: #f8fdf9;
        border: 1px solid #d4e6e0;
        border-radius: 4px;
        margin: 15px 0;
    }
    .scenario-title {
        font-size: 16px;
        font-weight: 700;
        color: #1f8e72;
        margin: 15px 0 10px 0;
    }
    .cdia-context, .cdia-driver, .cdia-impact, .cdia-action {
        font-size: 15px;
        line-height: 1.6;
        margin: 15px 0;
        padding: 15px;
        background-color: #ffffff;
        border-left: 4px solid #1f8e72;
        border-radius: 4px;
    }
    .cdia-context { border-left-color: #1f8e72; }
    .cdia-driver { border-left-color: #2a9d7f; }
    .cdia-impact { border-left-color: #3aac8e; }
    .cdia-action { border-left-color: #4abb9d; }
    .cdia-label {
        font-weight: 700;
        color: #1f8e72;
        font-size: 14px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

    # ========================================================================
    # 기본 정보
    # ========================================================================

    st.markdown(f"### {st.session_state.corp_name_result} 리스크 시나리오 분석")
    st.markdown("---")

    st.success("""
    💡 **소비재 산업 특화 스트레스 테스트**

    글로벌 공급망, 재고 관리, 인수합병, 유통 리스크 등 소비재 기업이 직면할 수 있는
    4가지 대표 위기 시나리오를 시뮬레이션합니다. 정량 재무 지표 변동과 정성적 리스크 요소를
    결합하여 회복력을 종합 평가합니다.
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
    # 소비재 산업 4대 시나리오 선택
    # ========================================================================

    show_section_header("🎯 소비재 위기 시나리오 선택")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    selected_scenario = None

    with col1:
        if st.button("🌍 글로벌 공급망 붕괴 및 원자재 가격 급등",
                     use_container_width=True, key="supply_chain"):
            selected_scenario = "supply_chain"

    with col2:
        if st.button("📦 트렌드 이탈로 인한 대규모 재고 누적",
                     use_container_width=True, key="inventory_accumulation"):
            selected_scenario = "inventory_accumulation"

    with col3:
        if st.button("💰 무리한 브랜드 인수로 인한 부채 쇼크",
                     use_container_width=True, key="brand_acquisition"):
            selected_scenario = "brand_acquisition"

    with col4:
        if st.button("⚖️ 전속 모델 리스크 및 유통망 소송 발생",
                     use_container_width=True, key="model_risk"):
            selected_scenario = "model_risk"

    st.markdown("")

    # ========================================================================
    # 선택된 시나리오 결과 - CDIA 프레임워크 적용
    # ========================================================================

    if selected_scenario:
        with st.spinner("소비재 산업 스트레스 테스트 실행 중..."):
            result = scenario_stress_test(financial_data, selected_scenario)

        # Session state에 결과 저장 (PDF 다운로드용)
        st.session_state.scenario_result = result

        # 시뮬레이션 분석 결과 텍스트 저장
        st.session_state.scenario_narrative = result.get('narrative_result', '')

        # 기업 맞춤형 Action Plan 저장
        st.session_state.action_plan_text = result.get('action_plan', '')

        scenario_name = result.get('scenario_name', '')
        scenario_desc = result.get('scenario_description', '')
        narrative = result.get('narrative_result', '')
        action_plan = result.get('action_plan', '')
        resilience = result.get('resilience', '')
        hybrid_original = result.get('hybrid_score_original', 0)
        hybrid_shocked = result.get('hybrid_score_shocked', 0)
        change_pct = result.get('change_percentage', 0)
        original_z = result.get('original_z_score', 0)
        shocked_z = result.get('shocked_z_score', 0)

        # ====================================================================
        # [1] 제목
        # ====================================================================
        show_section_header(f"📊 {scenario_name} 분석 결과")

        # ====================================================================
        # [2] 상단 지표 카드 (3개 병렬)
        # ====================================================================
        st.markdown("#### 📈 핵심 지표")

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric(
                label="기존 종합 점수",
                value=f"{hybrid_original:.1f}",
                delta=None,
                help="정량 80% + 정성 20%"
            )

        with metric_col2:
            st.metric(
                label="충격 후 종합 점수",
                value=f"{hybrid_shocked:.1f}",
                delta=f"{change_pct:+.1f}%",
                help="위기 시나리오 적용 후"
            )

        with metric_col3:
            st.metric(
                label="Z-Score 변동",
                value=f"{shocked_z:.2f}",
                delta=f"{original_z:.2f} → {shocked_z:.2f}",
                help=f"회복력: {resilience}"
            )

        st.markdown("---")

        # ====================================================================
        # [3] 기업 맞춤형 리스크 대응 권고사항 (상단)
        # ====================================================================
        st.markdown("#### 📋 기업 맞춤형 리스크 대응 권고사항")

        st.markdown(f"""
        <div class="scenario-detail-box">
        {action_plan.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ====================================================================
        # [4] CDIA 프레임워크 기반 상세 분석
        # ====================================================================
        st.markdown("#### 🔍 CDIA 분석 프레임워크")

        # Context
        context_text = {
            "supply_chain": "글로벌 공급망 이슈(물류 비용 급등, 원자재 가격 상승, 공급 차질 등)가 한국 소비재 기업의 수입 원재료 조달을 어렵게 하고, 동시에 생산원가를 급상승시키는 시장 환경을 가정합니다.",
            "inventory_accumulation": "소비자 트렌드 급변으로 기업의 기존 제품과 SKU에 대한 수요가 급격히 감소하고, 미처 처분하지 못한 재고자산이 누적되는 상황을 가정합니다.",
            "brand_acquisition": "기업이 과거에 M&A를 통해 대규모 브랜드를 인수했거나, 또는 인수하려는 계획 하에 높은 영업권이 계상된 상황에서 인수된 사업의 시너지가 기대에 미치지 못하는 환경을 가정합니다.",
            "model_risk": "제품 판매 시 전속 대리인 모델을 유지하고 있거나, 특정 유통 채널과의 계약 분쟁이 발생하는 상황에서 법적 소송이 동시다발적으로 진행되는 환경을 가정합니다."
        }

        st.markdown(f"""
        <div class="cdia-context">
        <div class="cdia-label">Context (위기 배경)</div>
        {context_text.get(selected_scenario, '')}
        </div>
        """, unsafe_allow_html=True)

        # Driver
        driver_text = {
            "supply_chain": "원자재 및 부품 수입 가격의 급등 → 원가 상승 → 이윤율 악화. 동시에 공급 차질로 인한 생산 차질 및 매출 기회 손실.",
            "inventory_accumulation": "매출 감소 → 재고 회전율 급저하. 판매 부진 제품의 적시 정리 미흡 → 유동성 악화. 추가 자산손상 인식 필요성 증가.",
            "brand_acquisition": "인수된 브랜드의 실적 부진 → 영업권 손상 인식 필요성 증가. 특수관계자 거래 및 이사회 통제 이슈 노출 위험.",
            "model_risk": "법적 분쟁 확대 → 현금 유출(소송비, 합의금) 가속화. 우발채무로 인한 신용 평가 하락."
        }

        st.markdown(f"""
        <div class="cdia-driver">
        <div class="cdia-label">Driver (촉발 요인)</div>
        {driver_text.get(selected_scenario, '')}
        </div>
        """, unsafe_allow_html=True)

        # Impact
        impact_text = f"""기존 종합 점수 {hybrid_original:.1f}에서 충격 후 {hybrid_shocked:.1f}로 변동 (변화율: {change_pct:+.1f}%).
        Z-Score는 {original_z:.2f}에서 {shocked_z:.2f}로 하락하여 회복력이 '【{resilience}】' 단계로 악화됩니다.

        정량적으로는 유동비율 및 현금흐름 악화가 주요 충격이며, 정성적으로는 DART 주석에 명시된 【{scenario_desc}】 리스크가 현실화될 경우 추가 손상을 입을 수 있습니다."""

        st.markdown(f"""
        <div class="cdia-impact">
        <div class="cdia-label">Impact (재무/정성 충격)</div>
        {impact_text}
        </div>
        """, unsafe_allow_html=True)

        # Action
        st.markdown(f"""
        <div class="cdia-action">
        <div class="cdia-label">Action (대응 방안)</div>
        {action_plan.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ====================================================================
        # [5] 회복력 판정 결과
        # ====================================================================
        st.markdown("#### 🏆 최종 회복력 판정")

        resilience_guide = {
            "견딜 수 있음": ("🟢", "Z > 2.99", "기업은 이 위기 상황에서 충분한 회복력을 보유하고 있습니다."),
            "위험": ("🟠", "1.81 < Z ≤ 2.99", "기업의 재무 건강도가 악화되어 주의가 필요합니다."),
            "심각": ("🔴", "Z ≤ 1.81", "기업은 심각한 재무 어려움에 직면할 수 있습니다.")
        }

        emoji, threshold, desc = resilience_guide.get(resilience, ("❓", "N/A", ""))

        st.markdown(f"""
        <div class="scenario-detail-box">
        <div style="text-align: center;">
            <div style="font-size: 20px; margin-bottom: 10px;">{emoji} <strong>{resilience}</strong></div>
            <div style="font-size: 14px; color: #666;">
                {threshold}<br>
                {desc}
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ====================================================================
        # 시나리오 미선택 상태
        # ====================================================================
        show_section_header("📋 소비재 산업 4대 위기 시나리오 개요")

        st.markdown("""
        | 시나리오 | 위험 요소 | 심각도 | 소비재 특화 |
        |---------|---------|-------|----------|
        | 🌍 글로벌 공급망 붕괴 | 원자재/부품 수급 차질 | 매우 높음 | 원가 압박, 공급선 다변화 실패 |
        | 📦 재고 누적 | 트렌드 이탈, 판매 부진 | 매우 높음 | 재고자산 손상차손, 유동성 위기 |
        | 💰 브랜드 인수 충격 | M&A 과다 레버리지 | 높음 | 영업권 손상, 특수관계자 거래 위험 |
        | ⚖️ 유통망 소송 | 전속모델 분쟁, 법적 리스크 | 중간 | 우발채무 현실화, 대금 지급 |

        **각 시나리오를 선택하여 해당 기업의 회복력을 종합 평가하세요.**
        """)

        st.success("""
        💡 **소비재 산업 리스크 평가 가이드**

        소비재 기업의 회복력은 정량 재무 지표(80%)와 산업 특화 정성 요소(20%)의 가중합으로 판정됩니다.
        **"견딜 수 있음"** 평가가 나올수록 위기 극복 능력이 우수하며, **"심각"** 등급은 즉각적인
        구조 개선이 필요함을 의미합니다.
        """)
