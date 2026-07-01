# -*- coding: utf-8 -*-
"""
기업 정량·정성 복합 리스크 검증 시스템 - 메인 진입점
Streamlit 탭 기반 애플리케이션 (병렬 처리 최적화)
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv
import concurrent.futures
from typing import TypedDict

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# 환경변수 로드
load_dotenv(".env")

# ✅ Streamlit Cloud Secrets 지원: st.secrets → os.environ 복사
# 배포 환경에서는 .env 파일이 없으므로, st.secrets에서 읽어서 os.environ에 설정
try:
    if "DART_API_KEY" in st.secrets:
        os.environ["DART_API_KEY"] = st.secrets["DART_API_KEY"]
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    # st.secrets가 없는 경우 (로컬 실행) 무시
    pass

# UI 헬퍼 임포트
from utils.ui_helpers import setup_page_config, apply_custom_css, initialize_session_state

# 뷰 함수 임포트
from views.dashboard_view import render_dashboard
from views.financial_view import render_financials
from views.qualitative_view import render_qualitative
from views.scenario_view import render_scenarios

# 분석 엔진 임포트
from utils.dart_api import (
    init_dart_api,
    search_company,
    get_periodic_report,
    extract_financial_statement,
    extract_notes
)
from utils.financial_analysis import financial_rule_engine
from utils.qualitative_analysis import (
    management_explanations,
    stakeholder_caveats,
    extract_risk_categories,
    extract_qualitative_risk_score
)
from utils.risk_scoring import integrate_final_risk_grade, get_financial_risk_trend
from utils.pdf_generator import generate_risk_report_pdf
from langchain_anthropic import ChatAnthropic


# ============================================================================
# TypedDict: PDF 리포트 데이터 구조 정의
# ============================================================================
class ReportDataDict(TypedDict, total=False):
    """
    PDF 생성에 필요한 모든 필드를 정의합니다.

    필수 필드:
    - corp_name: 기업명
    - report_date: 보고서 작성 일자
    - final_risk_score: 최종 위험 점수 (0~100)
    - final_risk_level: 최종 위험 등급 ("저위험"/"중위험"/"고위험")
    - final_risk_grade: 위험 등급 코드 ("LOW_RISK"/"MEDIUM_RISK"/"HIGH_RISK")
    - component_scores: 정량 분석 세부 점수
    - current_ratio: 유동비율
    - debt_ratio: 부채비율
    - risk_categories: 정성 리스크 카테고리
    - qualitative_risk_score: 정성 위험도 점수
    - scenario_result: 시나리오 분석 결과
    - scenario_narrative: 시나리오 서술형 분석
    - action_plan_text: 기업 맞춤형 액션 플랜
    """
    corp_name: str
    report_date: str
    final_risk_score: float
    final_risk_level: str
    final_risk_grade: str
    component_scores: dict
    current_ratio: float
    debt_ratio: float
    risk_categories: dict
    qualitative_risk_score: float
    scenario_result: dict
    scenario_narrative: str
    action_plan_text: str


# ============================================================================
# 페이지 설정
# ============================================================================

setup_page_config()
apply_custom_css()
initialize_session_state()


# ============================================================================
# 초기화 함수
# ============================================================================

def init_dart_and_llm():
    """DART API와 LLM을 초기화합니다."""
    try:
        dart = init_dart_api()
        st.session_state.dart = dart
    except ValueError as e:
        st.error(str(e))
        st.stop()

    api_key = os.getenv("Anthropic_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
        st.stop()

    try:
        llm = ChatAnthropic(
            api_key=api_key,
            model="claude-haiku-4-5-20251001",
            temperature=0.7,
            max_tokens=1024
        )
        st.session_state.llm = llm
    except Exception as e:
        st.error(f"❌ LLM 초기화 실패: {str(e)}")
        st.stop()


def perform_analysis():
    """기업 데이터를 수집하고 병렬 분석을 수행합니다."""
    dart = st.session_state.dart
    llm = st.session_state.llm
    company_name = st.session_state.company_name

    # 1. 기업 검색
    with st.spinner("기업 정보 조회 중..."):
        corp_code, corp_name_result = search_company(dart, company_name)

        if not corp_code:
            st.error(f"'{company_name}'을(를) 찾을 수 없습니다.")
            st.stop()

    # 2. 공시 조회
    with st.spinner("공시 정보 조회 중..."):
        report, report_type = get_periodic_report(dart, corp_code, corp_name_result)

        if report is None:
            st.error("정기 공시를 찾을 수 없습니다.")
            st.stop()

        rcept_no = report['rcept_no']
        rcept_dt = report['rcept_dt']

    # 3. 재무제표 추출
    with st.spinner("재무 데이터 추출 중..."):
        financial_df = extract_financial_statement(dart, corp_code)

        if financial_df is None or financial_df.empty:
            st.warning("재무제표 데이터를 찾을 수 없습니다.")
            financial_df = None

    # 4. 주석 추출
    with st.spinner("재무제표 주석 추출 중..."):
        notes = extract_notes(dart, rcept_no)

        if not notes:
            notes = "(주석 없음)"

    # 세션에 임시 저장
    st.session_state.corp_code = corp_code
    st.session_state.corp_name_result = corp_name_result
    st.session_state.report_type = report_type
    st.session_state.report_date = rcept_dt
    st.session_state.financial_df = financial_df
    st.session_state.notes = notes

    # 5. === 병렬 분석 (정량 + 정성 동시 실행) ===
    with st.spinner("정량·정성 분석 중 (병렬 처리)..."):

        def run_quantitative():
            """정량 분석"""
            return financial_rule_engine(financial_df)

        def run_qualitative_initial():
            """정성 분석 1단계: 경영진 설명 (정량 결과 필요 없음)"""
            return management_explanations(corp_name_result, {}, notes, llm)

        # ThreadPoolExecutor로 정량 + 정성(1단계) 병렬 실행
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_quantitative = executor.submit(run_quantitative)
            future_mgmt = executor.submit(run_qualitative_initial)

            # 둘 다 완료 대기
            analysis = future_quantitative.result()
            mgmt_response = future_mgmt.result()

        # 정성 분석 2단계: 이해관계자 검증 (정량 결과 필요)
        caveats = stakeholder_caveats(corp_name_result, mgmt_response, notes, analysis, llm)
        risk_categories = extract_risk_categories(caveats)
        qualitative_risk = extract_qualitative_risk_score(risk_categories)

    # 6. 최종 통합
    with st.spinner("최종 위험도 계산 중..."):
        final_risk = integrate_final_risk_grade(
            analysis['financial_risk_score'],
            qualitative_risk['qualitative_risk_score']
        )

    # 7. 5년 추세 조회
    with st.spinner("5년 위험도 추세 조회 중..."):
        try:
            trend_scores = get_financial_risk_trend(dart, corp_code)
        except Exception as e:
            st.warning(f"5년 추세 조회 오류: {e}")
            trend_scores = None

    # 세션 상태 저장
    st.session_state.analysis = analysis
    st.session_state.mgmt_response = mgmt_response
    st.session_state.caveats = caveats
    st.session_state.risk_categories = risk_categories
    st.session_state.qualitative_risk = qualitative_risk
    st.session_state.final_risk = final_risk
    st.session_state.trend_scores = trend_scores
    st.session_state.analysis_complete = True


# ============================================================================
# 메인 로직
# ============================================================================
# Force reload: 2026-07-01 14:30 - PDF Report Generation System integrated

if not st.session_state.get("analysis_complete", False):
    # === 초기 화면 ===
    st.html('<div class="deco-blob-1"></div><div class="deco-blob-2"></div><div class="hero-gradient"></div>')

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
            company_input = st.text_input(
                "기업명",
                value="",
                key="company_input",
                placeholder="",
                label_visibility="collapsed"
            )

        with col_btn:
            if st.button("분석", key="fetch_data", use_container_width=True):
                if company_input.strip():
                    st.session_state.company_name = company_input

                    # 초기화
                    if "dart" not in st.session_state:
                        init_dart_and_llm()

                    perform_analysis()
                    st.rerun()
                else:
                    st.error("기업명을 입력하세요")

        st.markdown(
            '<p class="disclaimer">본 분석은 공개 정보 기반의 정량 및 정성적 검증 시스템으로, 투자 의사결정의 보조 자료로만 활용하는 것을 권장드립니다.</p>',
            unsafe_allow_html=True
        )

else:
    # === 분석 완료 후 탭 기반 UI ===
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 분석 완료")
    st.sidebar.markdown(f"**기업**: {st.session_state.corp_name_result}")
    st.sidebar.markdown(f"**보고서**: {st.session_state.report_type} ({st.session_state.report_date})")

    if st.sidebar.button("🔄 새로운 검색", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.company_name = ""
        st.rerun()

    st.sidebar.markdown("---")

    # === PDF 다운로드 버튼 (안전한 데이터 바인딩) ===
    # 완전한 분석 데이터가 있을 때만 버튼 표시
    if all([
        st.session_state.get('corp_name_result'),
        st.session_state.get('final_risk'),
        st.session_state.get('analysis'),
        st.session_state.get('qualitative_risk')
    ]):
        st.sidebar.markdown("<hr style='margin: 10px 0;' />", unsafe_allow_html=True)

        # ✅ 최종 위험도 데이터 키 매핑
        # integrate_final_risk_grade()의 반환값:
        # - final_integrated_score → final_risk_score (PDF에서 사용)
        # - grade_label → final_risk_level (PDF에서 사용)
        # - final_risk_grade → final_risk_grade (변경 없음)
        final_risk_data = st.session_state.final_risk

        # 현재 화면의 모든 데이터를 딕셔너리로 캡처
        report_data: ReportDataDict = {
            "corp_name": st.session_state.corp_name_result,
            "report_date": st.session_state.report_date,
            # ✅ 수정된 키 매핑 (핵심!)
            "final_risk_score": final_risk_data.get('final_integrated_score', 0),
            "final_risk_level": final_risk_data.get('grade_label', '미판정'),
            "final_risk_grade": final_risk_data.get('final_risk_grade', '미판정'),
            "component_scores": st.session_state.analysis.get('component_scores', {}),
            "current_ratio": st.session_state.analysis.get('current_ratio', 0),
            "debt_ratio": st.session_state.analysis.get('debt_ratio', 0),
            "risk_categories": st.session_state.qualitative_risk.get('risk_categories', {}),
            "qualitative_risk_score": st.session_state.qualitative_risk.get('qualitative_risk_score', 0),
            "scenario_result": st.session_state.get('scenario_result'),
            "scenario_narrative": st.session_state.get('scenario_narrative', ''),
            "action_plan_text": st.session_state.get('action_plan_text', ''),
        }

        # 📊 [검증] 대시보드와 PDF의 최종 등급/점수 일치 확인
        st.sidebar.write("---")
        st.sidebar.caption("🔍 **데이터 검증:**")
        st.sidebar.caption(f"• 점수: {report_data['final_risk_score']:.1f}/100")
        st.sidebar.caption(f"• 등급: {report_data['final_risk_level']}")
        st.sidebar.caption(f"• 코드: {report_data['final_risk_grade']}")

        # PDF 생성 함수 (Re-run 안전성 확보)
        def generate_pdf_safe():
            try:
                return generate_risk_report_pdf(report_data)
            except Exception as e:
                st.sidebar.error(f"❌ PDF 생성 오류: {str(e)}")
                return None

        pdf_bytes = generate_pdf_safe()

        if pdf_bytes:
            st.sidebar.download_button(
                label="📄 경영진 보고용 종합 리스크 리포트 (.pdf)",
                data=pdf_bytes,
                file_name=f"{report_data['corp_name']}_리스크진단보고서_{report_data['report_date']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.sidebar.caption("✅ 대시보드 데이터 완벽 연동됨")
    else:
        st.sidebar.info("📌 기업 검색 및 분석을 먼저 완료해주세요.")

    # === 4개 탭 구조 ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 종합리스크대시보드",
        "📊 정량재무분석",
        "📝 정성적크로스체킹",
        "🎯 리스크시나리오"
    ])

    with tab1:
        render_dashboard()

    with tab2:
        render_financials()

    with tab3:
        render_qualitative()

    with tab4:
        render_scenarios()
