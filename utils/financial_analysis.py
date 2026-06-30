# -*- coding: utf-8 -*-
"""
재무 분석 엔진 모듈
정량 재무 분석, 리스크 점수 계산, 스트레스 테스트 기능 제공
"""

from typing import Optional, Dict, Any
import pandas as pd


def get_current_ratio_status(current_ratio: Optional[float]) -> Dict[str, str]:
    """유동비율 상태 평가 (3단계)"""
    if current_ratio is None:
        return {"status": "데이터 없음", "status_ko": "데이터 없음", "emoji": "❓"}

    if current_ratio >= 150:
        return {"status": "정상", "status_ko": "정상", "emoji": "🟢", "description": "단기 채무 지급 능력 양호"}
    elif current_ratio >= 100:
        return {"status": "주의", "status_ko": "주의", "emoji": "🟡", "description": "단기 유동성 개선 필요"}
    else:
        return {"status": "경고", "status_ko": "경고", "emoji": "🔴", "description": "단기 유동성 긴급 상태"}


def get_debt_ratio_status(debt_ratio: Optional[float]) -> Dict[str, str]:
    """부채비율 상태 평가 (3단계)"""
    if debt_ratio is None:
        return {"status": "데이터 없음", "status_ko": "데이터 없음", "emoji": "❓"}

    if debt_ratio <= 100:
        return {"status": "정상", "status_ko": "정상", "emoji": "🟢", "description": "재무 레버리지 양호"}
    elif debt_ratio <= 200:
        return {"status": "주의", "status_ko": "주의", "emoji": "🟡", "description": "부채 수준 주의 필요"}
    else:
        return {"status": "경고", "status_ko": "경고", "emoji": "🔴", "description": "부채 과다 상태"}


def get_revenue_quality_status(revenue_quality_score: float) -> Dict[str, str]:
    """매출 질 점수 상태 평가 (3단계)"""
    if revenue_quality_score <= 30:
        return {"status": "양호", "status_ko": "양호", "emoji": "🟢", "description": "현금 창출 능력 우수"}
    elif revenue_quality_score <= 60:
        return {"status": "주의", "status_ko": "주의", "emoji": "🟡", "description": "개선 필요"}
    else:
        return {"status": "경고", "status_ko": "경고", "emoji": "🔴", "description": "매출 질 악화"}


def get_liquidity_stress_status(liquidity_score: float) -> Dict[str, str]:
    """유동성 점수 상태 평가 (3단계)"""
    if liquidity_score <= 30:
        return {"status": "양호", "status_ko": "양호", "emoji": "🟢", "description": "유동성 안정"}
    elif liquidity_score <= 60:
        return {"status": "주의", "status_ko": "주의", "emoji": "🟡", "description": "개선 필요"}
    else:
        return {"status": "경고", "status_ko": "경고", "emoji": "🔴", "description": "유동성 악화"}


def get_leverage_risk_status(leverage_score: float) -> Dict[str, str]:
    """부채 점수 상태 평가 (3단계)"""
    if leverage_score <= 30:
        return {"status": "양호", "status_ko": "양호", "emoji": "🟢", "description": "부채 관리 우수"}
    elif leverage_score <= 60:
        return {"status": "주의", "status_ko": "주의", "emoji": "🟡", "description": "개선 필요"}
    else:
        return {"status": "경고", "status_ko": "경고", "emoji": "🔴", "description": "부채 위험"}


def get_overall_risk_status(risk_score: float) -> Dict[str, str]:
    """종합 위험도 상태 평가"""
    if risk_score < 40:
        return {"status": "우수", "status_ko": "우수", "emoji": "🟢", "description": "재무 건전"}
    elif risk_score < 70:
        return {"status": "양호", "status_ko": "양호", "emoji": "🟡", "description": "주의 필요"}
    else:
        return {"status": "위험", "status_ko": "위험", "emoji": "🔴", "description": "개선 시급"}


def find_account_value(data: Any, keywords: list) -> Optional[float]:
    """
    DataFrame 또는 dict에서 키워드 기반으로 계정값을 찾습니다.

    Args:
        data: 재무제표 DataFrame 또는 dict
        keywords: 검색할 계정명 키워드 리스트

    Returns:
        찾은 계정값 float 또는 None
    """
    try:
        if isinstance(data, pd.DataFrame):
            for keyword in keywords:
                for col in ['account_name', 'account_nm', 'acc_name', 'fs_nm', 'sj_nm', 'name']:
                    if col in data.columns:
                        match = data[data[col].astype(str).str.contains(keyword, na=False, case=False)]
                        if not match.empty:
                            for val_col in ['fs_amount', 'amount', 'fs_value', 'value', 'thstrm_amount']:
                                if val_col in match.columns:
                                    val = match.iloc[0][val_col]
                                    if pd.notna(val):
                                        return float(val)
        elif isinstance(data, dict):
            for keyword in keywords:
                for key, value in data.items():
                    if isinstance(key, str) and keyword.lower() in key.lower():
                        return float(value) if value else None
    except:
        pass

    return None


def financial_rule_engine(financial_df: Optional[pd.DataFrame], analysis_dict: Optional[Dict] = None) -> Dict:
    """
    정량 재무 분석 엔진
    매출 질, 유동성, 부채 비율을 평가하여 재무 위험도를 계산합니다.

    가중치:
    - 매출 질 (revenue_quality): 40%
    - 유동성 (liquidity_stress): 35%
    - 부채 비율 (leverage_risk): 25%

    Args:
        financial_df: 재무제표 DataFrame (utils.dart_api.extract_financial_statement() 결과)
        analysis_dict: 추가 분석 정보 (선택사항)

    Returns:
        {
            "financial_risk_score": float,     # 0-100 위험도 점수
            "risk_level": str,                 # "고위험" 또는 "정상"
            "component_scores": dict,          # 3가지 지표별 점수
            "detailed_findings": dict,         # 세부 분석 결과
            "debt_ratio": float,               # 부채비율 (%)
            "current_ratio": float             # 유동비율 (%)
        }
    """
    risk_scores = {
        "revenue_quality": 0,
        "liquidity_stress": 0,
        "leverage_risk": 0,
    }

    detailed_analysis = {}
    debt_ratio = None
    current_ratio = None

    # === 1단계: 매출 질 평가 ===
    try:
        if financial_df is not None:
            sales = find_account_value(financial_df, ['매출액', '매출', 'revenue', 'sales'])
            ar = find_account_value(financial_df, ['매출채권', '기타채권', 'receivable', 'ar'])
            ocf = find_account_value(financial_df, ['영업활동', '영업현금', 'operating', 'cash'])

            revenue_quality_score = 20

            if sales and ar:
                ar_turnover = sales / ar if ar > 0 else 0

                if ar_turnover < 2:
                    revenue_quality_score = 70
                    detailed_analysis["ar_warning"] = f"매출채권 회전율 저위: {ar_turnover:.2f}배"
                elif ar_turnover < 4:
                    revenue_quality_score = 50
                    detailed_analysis["ar_caution"] = f"매출채권 회전율 주의: {ar_turnover:.2f}배"
                else:
                    detailed_analysis["ar_quality"] = f"매출채권 회전율 양호: {ar_turnover:.2f}배"

            if ocf is not None:
                if ocf < 0:
                    revenue_quality_score = max(revenue_quality_score, 85)
                    detailed_analysis["ocf_warning"] = f"영업현금흐름 음수: {ocf:,.0f}원"
                else:
                    detailed_analysis["ocf_quality"] = f"영업현금흐름 양수: {ocf:,.0f}원"

            risk_scores["revenue_quality"] = revenue_quality_score
    except:
        risk_scores["revenue_quality"] = 40

    # === 2단계: 유동성 및 부채 리스크 평가 ===
    try:
        if financial_df is not None:
            current_assets = find_account_value(financial_df, ['유동자산', 'current assets'])
            current_liabilities = find_account_value(financial_df, ['유동부채', 'current liabilities'])
            total_assets = find_account_value(financial_df, ['자산총계', 'total assets'])
            total_debt = find_account_value(financial_df, ['부채총계', 'total liabilities'])

            # 유동성 평가
            liquidity_score = 20

            if current_assets is not None and current_liabilities is not None and current_liabilities > 0:
                current_ratio = (current_assets / current_liabilities) * 100

                if current_ratio < 100:
                    liquidity_score = 90
                    detailed_analysis["liquidity_risk"] = f"단기유동성 압박: {current_ratio:.1f}%"
                elif current_ratio < 150:
                    liquidity_score = 60
                    detailed_analysis["liquidity_caution"] = f"유동성 주의: {current_ratio:.1f}%"
                else:
                    detailed_analysis["liquidity_healthy"] = f"유동성 양호: {current_ratio:.1f}%"

            risk_scores["liquidity_stress"] = liquidity_score

            # 부채 평가
            leverage_score = 20

            if total_assets is not None and total_debt is not None:
                equity = total_assets - total_debt
                if equity > 0:
                    debt_ratio = (total_debt / equity) * 100

                    if debt_ratio > 200:
                        leverage_score = 80
                        detailed_analysis["leverage_high"] = f"부채비율 상승: {debt_ratio:.1f}%"
                    elif debt_ratio > 160:
                        leverage_score = 50
                        detailed_analysis["leverage_caution"] = f"부채비율 주의: {debt_ratio:.1f}%"
                    else:
                        detailed_analysis["leverage_healthy"] = f"부채비율 정상: {debt_ratio:.1f}%"

            risk_scores["leverage_risk"] = leverage_score
    except:
        risk_scores["liquidity_stress"] = 40
        risk_scores["leverage_risk"] = 40

    # === 4단계: 수익성 지표 계산 (ROE, ROA) ===
    roe = None
    roa = None

    try:
        if financial_df is not None:
            net_income = find_account_value(financial_df, ['당기순이익', '순이익', 'net_income'])
            total_equity = find_account_value(financial_df, ['자본총계', '자본', '총자본', 'total_equity', 'equity'])
            total_assets = find_account_value(financial_df, ['자산총계', '총자산', 'total_assets', 'assets'])

            if net_income and total_equity and total_equity > 0:
                roe = (net_income / total_equity) * 100

            if net_income and total_assets and total_assets > 0:
                roa = (net_income / total_assets) * 100

            if roe:
                detailed_analysis["roe_value"] = f"ROE(자기자본이익률): {roe:.2f}%"
            if roa:
                detailed_analysis["roa_value"] = f"ROA(총자산이익률): {roa:.2f}%"
    except:
        pass

    # === 5단계: 상태 평가 ===
    current_ratio_rounded = round(current_ratio, 1) if current_ratio else None
    debt_ratio_rounded = round(debt_ratio, 1) if debt_ratio else None

    current_ratio_status = get_current_ratio_status(current_ratio_rounded)
    debt_ratio_status = get_debt_ratio_status(debt_ratio_rounded)
    revenue_quality_status = get_revenue_quality_status(risk_scores["revenue_quality"])
    liquidity_stress_status = get_liquidity_stress_status(risk_scores["liquidity_stress"])
    leverage_risk_status = get_leverage_risk_status(risk_scores["leverage_risk"])

    # === 6단계: 종합 점수 계산 ===
    financial_risk_score = (
        risk_scores["revenue_quality"] * 0.40 +
        risk_scores["liquidity_stress"] * 0.35 +
        risk_scores["leverage_risk"] * 0.25
    )

    overall_risk_status = get_overall_risk_status(financial_risk_score)

    return {
        "financial_risk_score": round(financial_risk_score, 1),
        "risk_level": "고위험" if financial_risk_score >= 70 else "정상",
        "component_scores": risk_scores,
        "detailed_findings": detailed_analysis,
        "debt_ratio": debt_ratio_rounded,
        "current_ratio": current_ratio_rounded,
        "current_ratio_status": current_ratio_status,
        "debt_ratio_status": debt_ratio_status,
        "revenue_quality_status": revenue_quality_status,
        "liquidity_stress_status": liquidity_stress_status,
        "leverage_risk_status": leverage_risk_status,
        "overall_risk_status": overall_risk_status,
        "roe": round(roe, 2) if roe else None,
        "roa": round(roa, 2) if roa else None
    }


def _calculate_z_score_from_financial_data(financial_data: Dict) -> float:
    """
    재무 데이터로부터 Z-Score를 계산합니다.

    financial_rule_engine()의 로직을 기반으로 risk_scores를 계산하고,
    이를 Z-Score(0-4 범위)로 변환합니다.

    Args:
        financial_data: 재무 지표 dict
            - ar_turnover: 매출채권 회전율
            - operating_cash_flow: 영업현금흐름
            - liquidity_ratio: 유동비율
            - debt_ratio: 부채비율

    Returns:
        float: Z-Score (0-4 범위)
            Z > 2.99: "견딜 수 있음" (안전)
            1.81 < Z <= 2.99: "위험" (그레이존)
            Z <= 1.81: "심각" (위기)
    """

    risk_scores = {
        "revenue_quality": 20,
        "liquidity_stress": 20,
        "leverage_risk": 20,
    }

    # Revenue Quality 점수 계산
    try:
        ar_turnover = financial_data.get("ar_turnover")
        ocf = financial_data.get("operating_cash_flow")

        revenue_quality_score = 20

        if ar_turnover is not None:
            if ar_turnover < 2:
                revenue_quality_score = 70
            elif ar_turnover < 4:
                revenue_quality_score = 50
            else:
                revenue_quality_score = 20

        if ocf is not None and ocf < 0:
            revenue_quality_score = max(revenue_quality_score, 85)

        risk_scores["revenue_quality"] = revenue_quality_score
    except:
        pass

    # Liquidity Stress 점수 계산
    try:
        liquidity_ratio = financial_data.get("liquidity_ratio")

        liquidity_score = 20

        if liquidity_ratio is not None:
            if liquidity_ratio < 100:
                liquidity_score = 90
            elif liquidity_ratio < 150:
                liquidity_score = 60
            else:
                liquidity_score = 20

        risk_scores["liquidity_stress"] = liquidity_score
    except:
        pass

    # Leverage Risk 점수 계산
    try:
        debt_ratio = financial_data.get("debt_ratio")

        leverage_score = 20

        if debt_ratio is not None:
            if debt_ratio > 200:
                leverage_score = 80
            elif debt_ratio > 160:
                leverage_score = 50
            else:
                leverage_score = 20

        risk_scores["leverage_risk"] = leverage_score
    except:
        pass

    # 종합 financial_risk_score 계산 (0-100)
    financial_risk_score = (
        risk_scores["revenue_quality"] * 0.40 +
        risk_scores["liquidity_stress"] * 0.35 +
        risk_scores["leverage_risk"] * 0.25
    )

    # Z-Score로 변환 (0-4 범위)
    # risk_score 0 → z_score 4 (안전)
    # risk_score 100 → z_score 0 (위기)
    z_score = 4 - (financial_risk_score / 25)

    return z_score


def scenario_stress_test(financial_data: Dict, scenario: str) -> Dict:
    """
    과거 위기 시나리오에 충격 계수를 적용하여 스트레스 테스트를 수행합니다.

    각 시나리오별로 재무 지표에 충격을 적용하고, 변화된 Z-Score를 계산합니다.

    Args:
        financial_data: 재무 지표 dict
            {
                "debt_ratio": 부채비율(%),
                "liquidity_ratio": 유동비율(%),
                "ar_turnover": 매출채권 회전율(배),
                "operating_cash_flow": 영업현금흐름(원),
                "net_income": 순이익(원),
                ...
            }
        scenario: "crisis_2008" | "covid19" | "rate_hike" | "industry_decline"

    Returns:
        {
            "scenario": str,                      # 선택된 시나리오
            "scenario_name": str,                 # 시나리오 한글명
            "shocked_metrics": dict,              # 충격 적용된 지표들
            "original_z_score": float,            # 기존 Z-Score
            "shocked_z_score": float,             # 시나리오 적용 후 Z-Score
            "resilience": str,                    # "견딜 수 있음" | "위험" | "심각"
            "change_percentage": float,           # Z-Score 변화율(%)
            "recommendation": str                 # 결론 및 권고사항
        }
    """

    shock_scenarios = {
        "crisis_2008": {
            "debt_ratio": 1.3,             # +30%
            "liquidity_ratio": 0.7,        # -30%
            "ar_turnover": 0.9,            # -10%
            "operating_cash_flow": 0.8,    # -20%
            "net_income": 0.7              # -30%
        },
        "covid19": {
            "debt_ratio": 1.1,             # +10%
            "liquidity_ratio": 0.85,       # -15%
            "ar_turnover": 0.9,            # -10%
            "operating_cash_flow": 0.6,    # -40%
            "net_income": 0.65             # -35%
        },
        "rate_hike": {
            "debt_ratio": 1.15,            # +15%
            "liquidity_ratio": 0.8,        # -20%
            "ar_turnover": 0.95,           # -5%
            "operating_cash_flow": 0.9,    # -10%
            "net_income": 0.85             # -15%
        },
        "industry_decline": {
            "debt_ratio": 1.1,             # +10%
            "liquidity_ratio": 0.85,       # -15%
            "ar_turnover": 0.85,           # -15%
            "operating_cash_flow": 0.7,    # -30%
            "net_income": 0.75             # -25%
        }
    }

    scenario_names = {
        "crisis_2008": "2008년 금융위기",
        "covid19": "COVID-19 팬데믹",
        "rate_hike": "금리 상승",
        "industry_decline": "산업 침체"
    }

    if scenario not in shock_scenarios:
        return {"error": f"Unknown scenario: {scenario}"}

    shocks = shock_scenarios[scenario]
    scenario_name = scenario_names.get(scenario, scenario)

    # 기존 Z-Score 계산
    original_z_score = _calculate_z_score_from_financial_data(financial_data)

    # 충격 계수 적용하여 shocked_metrics 생성
    shocked_metrics = {}
    for key, value in financial_data.items():
        if key in shocks and value is not None:
            shocked_metrics[key] = value * shocks[key]
        else:
            shocked_metrics[key] = value

    # 변화된 Z-Score 계산
    shocked_z_score = _calculate_z_score_from_financial_data(shocked_metrics)

    # Z-Score 변화율 계산
    if original_z_score > 0:
        change_percentage = ((shocked_z_score - original_z_score) / original_z_score) * 100
    else:
        change_percentage = 0

    # Resilience 판정
    if shocked_z_score > 2.99:
        resilience = "견딜 수 있음"
        resilience_detail = "기업은 이 위기 상황에서 충분한 회복력을 보유하고 있습니다."
    elif shocked_z_score > 1.81:
        resilience = "위험"
        resilience_detail = "기업의 재무 건강도가 악화되어 주의가 필요합니다."
    else:
        resilience = "심각"
        resilience_detail = "기업은 이 위기 상황에서 심각한 재무 어려움에 직면할 수 있습니다."

    # 권고사항 생성
    recommendation = (
        f"【{scenario_name}】 시나리오 스트레스 테스트 결과:\n\n"
        f"▸ 기존 Z-Score: {original_z_score:.2f}\n"
        f"▸ 시나리오 적용 후 Z-Score: {shocked_z_score:.2f}\n"
        f"▸ 변화율: {change_percentage:+.1f}%\n"
        f"▸ 회복력 평가: 【{resilience}】\n\n"
        f"{resilience_detail}\n\n"
        f"기업은 다음과 같은 사항을 점검하시기 바랍니다:\n"
        f"① 부채 관리 및 이자비용 커버율 개선\n"
        f"② 운영현금흐름 안정성 확보\n"
        f"③ 유동성 버퍼(현금성자산) 확충\n"
        f"④ 매출채권 관리 개선"
    )

    return {
        "scenario": scenario,
        "scenario_name": scenario_name,
        "shocked_metrics": shocked_metrics,
        "original_z_score": round(original_z_score, 2),
        "shocked_z_score": round(shocked_z_score, 2),
        "resilience": resilience,
        "change_percentage": round(change_percentage, 1),
        "recommendation": recommendation
    }
