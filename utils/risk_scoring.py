# -*- coding: utf-8 -*-
"""
위험도 통합 및 시나리오 분석 모듈
정량·정성 위험도 가중 통합, 5년 재무 추세 분석
"""

from typing import Optional, Dict, Any, Tuple
import pandas as pd
from datetime import datetime
import time


def integrate_final_risk_grade(financial_risk_score: float, qualitative_risk_score: float) -> Dict:
    """
    정량 위험도(재무 분석)와 정성 위험도를 가중치로 통합하여 최종 위험 등급을 산출합니다.

    가중치:
    - 정량(financial_rule_engine): 60%
    - 정성(qualitative_analysis): 40%

    최종 점수 = (financial_risk_score × 0.6) + (qualitative_risk_score × 0.4)

    Args:
        financial_risk_score: 정량 위험도 점수 (0-100) from financial_rule_engine()
        qualitative_risk_score: 정성 위험도 점수 (0-100) from extract_qualitative_risk_score()

    Returns:
        {
            "final_integrated_score": float,           # 최종 통합 점수 (0-100)
            "final_risk_grade": str,                   # "HIGH_RISK" | "MEDIUM_RISK" | "LOW_RISK"
            "color": str,                              # "red" | "orange" | "green"
            "grade_label": str,                        # "고위험" | "중위험" | "저위험"
            "explanation": str                         # 최종 판정 근거
        }

    판정 기준:
    - final_score > 70: HIGH_RISK (red) → "고위험"
    - 50 < final_score <= 70: MEDIUM_RISK (orange) → "중위험"
    - final_score <= 50: LOW_RISK (green) → "저위험"
    """

    # 최종 통합 점수 계산
    final_integrated_score = (financial_risk_score * 0.6) + (qualitative_risk_score * 0.4)

    # 최종 등급 및 색상 결정
    if final_integrated_score > 70:
        final_risk_grade = "HIGH_RISK"
        color = "red"
        grade_label = "고위험"
    elif final_integrated_score > 50:
        final_risk_grade = "MEDIUM_RISK"
        color = "orange"
        grade_label = "중위험"
    else:
        final_risk_grade = "LOW_RISK"
        color = "green"
        grade_label = "저위험"

    # 설명 생성
    explanation = (
        f"정량 위험도: {financial_risk_score:.1f}/100 (가중치 60%), "
        f"정성 위험도: {qualitative_risk_score:.1f}/100 (가중치 40%)을 "
        f"종합하여 최종 등급 【{grade_label}】으로 판정됩니다."
    )

    return {
        "final_integrated_score": round(final_integrated_score, 1),
        "final_risk_grade": final_risk_grade,
        "color": color,
        "grade_label": grade_label,
        "explanation": explanation
    }


def get_financial_risk_trend(dart: Any, corp_code: str) -> Dict:
    """
    5개년(2020-2024)의 실제 재무 위험도 추세를 DART API로 조회합니다.

    각 연도의 재무제표를 추출하여 financial_rule_engine()으로 위험도를 계산합니다.

    Args:
        dart: OpenDartReader 인스턴스
        corp_code: 기업 코드

    Returns:
        {
            2020: 35.2,
            2021: 38.5,
            2022: 40.1,
            2023: 42.3,
            2024: 32.0,
            "status": "완료" | "부분" | "오류"
        }

    Note:
        이 함수는 financial_analysis.financial_rule_engine()을 사용하므로,
        필요시 import해서 사용해야 합니다.
    """
    from utils.financial_analysis import financial_rule_engine

    trend_scores = {}
    years = [2020, 2021, 2022, 2023, 2024]
    success_count = 0
    error_count = 0

    for year in years:
        try:
            year_str = str(year)

            # DART에서 해당 연도 재무제표 조회
            fs_data = dart.finstate_all(corp_code, year_str)

            if fs_data is None or fs_data.empty:
                trend_scores[year] = None
                error_count += 1
            else:
                # 위험도 점수 계산 (financial_rule_engine 재사용)
                analysis = financial_rule_engine(fs_data)
                trend_scores[year] = round(analysis['financial_risk_score'], 1)
                success_count += 1

            # API 호출 제한 회피 (연도별 1초 대기)
            time.sleep(1)

        except Exception as e:
            # 개별 연도 오류는 무시하고 계속 진행
            trend_scores[year] = None
            error_count += 1

    # 조회 상태 판정
    if success_count == 5:
        status = "완료"
    elif success_count > 0:
        status = "부분"
    else:
        status = "오류"

    trend_scores["status"] = status
    return trend_scores
