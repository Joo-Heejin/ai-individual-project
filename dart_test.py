# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from utils.dart_api import (
    init_dart_api,
    search_company,
    get_periodic_report,
    extract_financial_statement,
    extract_notes_from_document
)
from utils.financial_analysis import (
    financial_rule_engine
)
from utils.qualitative_analysis import (
    management_explanations,
    stakeholder_caveats,
    extract_risk_categories,
    extract_qualitative_risk_score
)
from utils.risk_scoring import (
    integrate_final_risk_grade,
    get_financial_risk_trend
)
from langchain_anthropic import ChatAnthropic

sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("🔄 DART API + 정성분석 통합 테스트")
print("💡 최초 실행 시 데이터 다운로드로 인해 30초~1분 정도 소요될 수 있습니다.")
print("   잠시만 기다려주세요...")
print("="*60 + "\n")

# 환경변수 로드
load_dotenv(".env")

# LLM 초기화
api_key = os.getenv("Anthropic_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("⚠️  ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    print("   정성 분석은 스킵합니다.")
    llm = None
else:
    try:
        llm = ChatAnthropic(
            api_key=api_key,
            model="claude-haiku-4-5-20251001",
            temperature=0.7,
            max_tokens=1024
        )
        print("✅ Claude LLM 초기화 완료\n")
    except Exception as e:
        print(f"⚠️  LLM 초기화 실패: {e}")
        llm = None

# OpenDartReader 초기화
try:
    dart = init_dart_api()
    print("✅ OpenDartReader 초기화 완료\n")
except Exception as e:
    print(f"❌ OpenDartReader 초기화 실패: {e}")
    exit(1)


# 메인 실행
if __name__ == "__main__":
    try:
        # 1. 기업 검색
        print(f"🔍 기업 검색 중: '하이브'...")
        corp_code, corp_name = search_company(dart, "하이브")

        if corp_code:
            print(f"✅ 기업 발견: {corp_name} (코드: {corp_code})\n")
        else:
            print("💡 '삼성전자'로 재검색 중...\n")
            print(f"🔍 기업 검색 중: '삼성전자'...")
            corp_code, corp_name = search_company(dart, "삼성전자")
            if corp_code:
                print(f"✅ 기업 발견: {corp_name} (코드: {corp_code})\n")

        if not corp_code:
            raise ValueError("검색 실패")

        # 2. 정기 공시 조회 (사업보고서 우선)
        print(f"📋 {corp_name}의 정기 공시 검색 중...")
        report, report_type = get_periodic_report(dart, corp_code, corp_name)

        if report is None:
            raise ValueError("정기 공시 조회 실패")

        rcept_no = report['rcept_no']
        rcept_dt = report['rcept_dt']
        report_nm = report['report_nm']
        print(f"✅ {report_type} 발견: {report_nm} (접수: {rcept_dt})\n")

        # 3. 재무제표 추출
        print("📊 재무제표 추출 중...\n")
        financial_df = extract_financial_statement(dart, corp_code)

        if financial_df is not None:
            print("📌 재무제표 데이터 (상위 10줄):")
            print("-" * 80)
            print(financial_df.head(10).to_string())
            print("-" * 80)
            print(f"총 {len(financial_df)}개 항목\n")
        else:
            print("⚠️  재무제표 데이터가 없습니다.\n")

        # 3-1. 재무 분석 (정량 분석)
        print("📊 정량 재무 분석 중...\n")
        if financial_df is not None:
            analysis = financial_rule_engine(financial_df)
            print("📌 정량 분석 결과:")
            print("-" * 80)
            print(f"• 종합 위험도: {analysis['financial_risk_score']}/100")
            print(f"• 위험 수준: {analysis['risk_level']}")
            print(f"• 매출 질 점수: {analysis['component_scores']['revenue_quality']}/100")
            print(f"• 유동성 점수: {analysis['component_scores']['liquidity_stress']}/100")
            print(f"• 부채 점수: {analysis['component_scores']['leverage_risk']}/100")
            if analysis['current_ratio']:
                print(f"• 유동비율: {analysis['current_ratio']:.1f}%")
            if analysis['debt_ratio']:
                print(f"• 부채비율: {analysis['debt_ratio']:.1f}%")
            print("\n세부 분석:")
            for key, value in analysis['detailed_findings'].items():
                print(f"  - {value}")
            print("-" * 80)
            print()

        # 4. 재무제표 주석 추출
        print("📝 재무제표 주석 추출 중...\n")
        notes = extract_notes_from_document(dart, rcept_no)

        if notes:
            print("📌 재무제표 주석 텍스트 (처음 500자):")
            print("-" * 80)
            print(notes[:500] + "...")
            print("-" * 80)
            print(f"총 {len(notes)}자\n")

        # 5. 정성 분석 (LLM 기반)
        if llm:
            print("🤖 정성적 리스크 분석 진행 중...\n")

            # 5-1. 경영진 설명 생성
            print("💼 경영진 관점 설명 생성 중...")
            mgmt_response = management_explanations(corp_name, analysis, notes if notes else "(주석 없음)", llm)
            print("✅ 경영진 설명 생성 완료\n")

            # 5-2. 이해관계자 검증
            print("⚖️ 이해관계자 검증 중...")
            caveats = stakeholder_caveats(corp_name, mgmt_response, notes if notes else "(주석 없음)", analysis, llm)
            print("✅ 이해관계자 검증 완료\n")

            # 5-3. 리스크 카테고리 추출
            print("📊 리스크 카테고리 추출 중...")
            risk_categories = extract_risk_categories(caveats)
            print("✅ 리스크 카테고리 추출 완료\n")

            # 5-4. 정성 위험도 점수 계산
            print("📈 정성 위험도 점수 계산 중...")
            qualitative_risk = extract_qualitative_risk_score(risk_categories)
            print("✅ 정성 위험도 점수 계산 완료\n")

            # 결과 출력
            print("="*60)
            print("📊 정성적 분석 결과")
            print("="*60)
            print(f"정성 위험도: {qualitative_risk['qualitative_risk_score']}/100")
            print(f"발견된 리스크 카테고리: {qualitative_risk['risk_count']}개")
            print(f"\n세부 점수:")
            print(f"  • 우발채무: {qualitative_risk['scoring_details']['contingent_score']}/45")
            print(f"  • 특수관계자거래: {qualitative_risk['scoring_details']['related_score']}/40")
            print(f"  • 자산손상: {qualitative_risk['scoring_details']['asset_score']}/40")
            print(f"  • 투자평가: {qualitative_risk['scoring_details']['assessment_score']}/25")
            print("="*60 + "\n")

            # 6. 최종 위험도 통합
            print("🔄 최종 위험도 통합 중...")
            final_risk = integrate_final_risk_grade(
                analysis['financial_risk_score'],
                qualitative_risk['qualitative_risk_score']
            )
            print("✅ 최종 위험도 통합 완료\n")

            # 최종 통합 결과 출력
            print("="*60)
            print("📊 최종 리스크 판정")
            print("="*60)
            print(f"정량 위험도: {analysis['financial_risk_score']}/100 (가중치 60%)")
            print(f"정성 위험도: {qualitative_risk['qualitative_risk_score']}/100 (가중치 40%)")
            print(f"\n【최종 통합 점수】: {final_risk['final_integrated_score']}/100")
            print(f"【최종 위험 등급】: {final_risk['grade_label']}")
            print(f"【평가】: {final_risk['explanation']}")
            print("="*60 + "\n")

        # 7. 5년 위험도 추세 분석
        print("📈 5년 위험도 추세 분석 중...\n")
        try:
            trend_scores = get_financial_risk_trend(dart, corp_code)

            print("="*60)
            print("📊 5년 재무 위험도 추세 (DART 공시 기반)")
            print("="*60)

            if trend_scores.get("status") != "오류":
                years = [2020, 2021, 2022, 2023, 2024]
                print("\n연도별 위험도 점수:")
                for year in years:
                    score = trend_scores.get(year)
                    if score is not None:
                        status = "✅" if score < 50 else "⚠️" if score < 70 else "🚨"
                        print(f"  {year}년: {score}/100 {status}")
                    else:
                        print(f"  {year}년: 데이터 없음")

                print(f"\n조회 상태: {trend_scores.get('status')}")

                # 추세 분석
                valid_scores = [score for score in trend_scores.values()
                               if isinstance(score, (int, float)) and score is not None]
                if len(valid_scores) > 1:
                    latest = valid_scores[-1]
                    earliest = valid_scores[0]
                    change = latest - earliest

                    print(f"\n추세 분석:")
                    print(f"  • 최초 (2020년): {earliest:.1f}/100")
                    print(f"  • 최근 (2024년): {latest:.1f}/100")
                    print(f"  • 변화도: {change:+.1f} ({'개선' if change < 0 else '악화'})")
            else:
                print("⚠️ 5년 데이터 조회 실패")

            print("="*60 + "\n")
        except Exception as e:
            print(f"⚠️ 5년 추세 분석 오류: {e}\n")

        # 완료 메시지
        print("="*60)
        print("✅ 전체 분석 완료!")
        print("="*60 + "\n")

    except Exception as e:
        import traceback
        print(f"\n❌ 오류 발생: {e}\n")
        traceback.print_exc()
        exit(1)
