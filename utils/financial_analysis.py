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


def _calculate_qualitative_risk_score(scenario: str) -> float:
    """
    시나리오별 정성 리스크 점수를 계산합니다.
    소비재 산업 특화 정성 요소를 반영하여 추가 위험도를 산출합니다.

    Args:
        scenario: "supply_chain" | "inventory_accumulation" | "brand_acquisition" | "model_risk"

    Returns:
        float: 정성 리스크 점수 (0-30 범위, 높을수록 위험)
    """
    qualitative_scores = {
        "supply_chain": 25,          # 공급망 붕괴: DART 공급선 다변화 리스크 강제 반영
        "inventory_accumulation": 28, # 재고 누적: 재고자산 손상차손 최고위험
        "brand_acquisition": 30,      # 브랜드 인수: 영업권 손상 및 특수관계자 거래 위험 최대
        "model_risk": 22              # 유통망 소송: 우발채무 및 소송 리스크 반영
    }
    return qualitative_scores.get(scenario, 0)


def _generate_action_plan(financial_data: Dict, scenario: str, resilience: str) -> str:
    """
    기업의 실제 재무 지표와 회복력 등급을 기반으로 맞춤형 대응 방안을 생성합니다.

    [축 A: 유동비율 기준] + [축 B: 시나리오별 정성 리스크] 조합으로 동적 생성

    Args:
        financial_data: 기업의 재무 지표
        scenario: 시나리오 ("supply_chain" | "inventory_accumulation" | "brand_acquisition" | "model_risk")
        resilience: 회복력 등급 ("견딜 수 있음" | "위험" | "심각")

    Returns:
        str: 기업 맞춤형 Action Plan 텍스트
    """

    # 축 A: 유동비율 판단
    liquidity_ratio = financial_data.get('liquidity_ratio', 150)

    if liquidity_ratio >= 150:
        liquidity_stance = "기업은 기존 유동비율이 양호하여 단기적인 재무 버퍼를 보유하고 있습니다. 따라서 자산 매각 같은 극단적 조치보다는, 본 위기 시나리오 발생 시 보유 유동성을 활용한 전략적 기회 포착이 가능합니다."
        liquidity_action = "• 위기 국면에서의 공급망 강화 투자 또는 M&A 기회 포착\n• 마케팅 및 브랜드 강화 자금 추가 배분\n• 장기적 경쟁력 확보를 위한 R&D 투자 확대"
    elif liquidity_ratio >= 100:
        liquidity_stance = "기업의 유동성이 보통 수준으로 정상 범위를 유지하고 있습니다. 위기 발생 시 적절한 속도의 유동성 관리가 필수적입니다."
        liquidity_action = "• 운전자본(재고, 매출채권) 회전율 최적화\n• 불필요한 설비투자 일시 중단\n• 단기차입금 리파이낸싱 계획 수립"
    else:
        liquidity_stance = "기업은 현재 단기 지급 능력이 한계에 도달해 있어 시나리오 충격 발생 시 즉각적인 디폴트 리스크가 존재합니다. 극도의 조치가 필수적입니다."
        liquidity_action = "• 비핵심 자산의 신속한 유동화 (매각/담보화)\n• 운전자본(재고/매출채권)의 강제적 단축\n• 차입금 구조조정 및 선제적 유동성 확보"

    # 축 B: 시나리오별 정성 리스크 Action
    scenario_actions = {
        "supply_chain": "• 공급선 다변화 전략 재정비 (신규 협력사 발굴)\n• 전략적 재고 비축 정책 도입\n• 원가 경쟁력 강화를 위한 구조조정",
        "inventory_accumulation": "• 재고자산의 실시간 진부화 평가 점검\n• 판매 부진 SKU의 즉시 정리 및 슬림화\n• 유통 채널별 재고 최적화 및 반품 정책 재정의",
        "brand_acquisition": "• 피인수 기업(또는 인수 대상)의 시너지 재평가\n• 영업권 손상 징후 사전 점검 및 충당금 확충\n• 특수관계자 거래의 투명성 강화 및 감시",
        "model_risk": "• 계류 중인 소송의 조기 합의 프로세스 가동\n• 사전 법무 리스크 충당금 확충\n• 전속 계약의 법적 리스크 점검 및 재정비"
    }

    scenario_action = scenario_actions.get(scenario, "")

    # 회복력 등급별 추가 강조
    resilience_emphasis = {
        "견딜 수 있음": "현재 회복력이 양호하므로 선제적이고 장기적인 관점의 대응이 효과적입니다.",
        "위험": "회복력이 약화되었으므로 즉시적이고 강도 높은 대응이 필수적입니다.",
        "심각": "회복력이 극도로 악화되어 긴급한 구조 개선 없이는 기업 존속이 위협받을 수 있습니다."
    }

    resilience_msg = resilience_emphasis.get(resilience, "")

    # 최종 통합 텍스트
    action_plan = f"""
【대응 전략 개요】

{liquidity_stance}

{resilience_msg}

【즉시 실행 과제】

{liquidity_action}

【시나리오별 전문 대응】

{scenario_action}

【종합 권고】

위 과제들을 우선순위별로 분류하여 이사회 및 경영진 회의에서 즉시 논의하고, 분기별 실행 체크리스트로 관리할 것을 권장합니다. 특히 유동성 악화 기업의 경우 향후 3개월 내 실행 계획을 확정하고 월별 모니터링을 통해 진행 상황을 점검해야 합니다.
"""

    return action_plan.strip()


def scenario_stress_test(financial_data: Dict, scenario: str) -> Dict:
    """
    소비재 산업 특화 스트레스 테스트를 수행합니다.
    정량 지표 충격 + 정성 리스크 가중 합산으로 하이브리드 회복력 평가.

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
        scenario: "supply_chain" | "inventory_accumulation" | "brand_acquisition" | "model_risk"

    Returns:
        {
            "scenario": str,                      # 선택된 시나리오
            "scenario_name": str,                 # 시나리오 한글명
            "scenario_description": str,          # 정성 연동 설명
            "original_z_score": float,            # 기존 Z-Score (정량)
            "qualitative_score": float,           # 정성 리스크 점수
            "shocked_z_score": float,             # 충격 후 Z-Score (정량)
            "hybrid_score": float,                # 하이브리드 최종 점수 (정량 + 정성)
            "resilience": str,                    # "견딜 수 있음" | "위험" | "심각"
            "change_percentage": float,           # 하이브리드 점수 변화율(%)
            "narrative_result": str               # 투자 보고서 형식의 통합 결과 문단
        }
    """

    shock_scenarios = {
        "supply_chain": {
            "debt_ratio": 1.2,             # +20%
            "liquidity_ratio": 0.75,       # -25%
            "operating_cash_flow": 0.7,    # -30%
            "net_income": 0.8              # -20%
        },
        "inventory_accumulation": {
            "ar_turnover": 0.6,            # -40%
            "liquidity_ratio": 0.85,       # -15%
            "operating_cash_flow": 0.8,    # -20%
        },
        "brand_acquisition": {
            "debt_ratio": 1.5,             # +50%
            "liquidity_ratio": 0.7,        # -30%
        },
        "model_risk": {
            "operating_cash_flow": 0.85,   # -15%
            "net_income": 0.9              # -10%
        }
    }

    scenario_names = {
        "supply_chain": "글로벌 공급망 붕괴 및 원자재 가격 급등",
        "inventory_accumulation": "트렌드 이탈로 인한 대규모 재고 누적",
        "brand_acquisition": "무리한 브랜드 인수로 인한 부채 쇼크",
        "model_risk": "전속 모델 리스크 및 유통망 소송 발생"
    }

    scenario_qualitative = {
        "supply_chain": "공급선 다변화 실패 및 원가 압박 리스크",
        "inventory_accumulation": "DART 주석상 재고자산 및 유통 자산손상차손",
        "brand_acquisition": "특수관계자 거래 리스크 및 영업권(Goodwill) 손상",
        "model_risk": "DART 주석 내 우발채무 및 계류 중인 소송 위험"
    }

    if scenario not in shock_scenarios:
        return {"error": f"Unknown scenario: {scenario}"}

    shocks = shock_scenarios[scenario]
    scenario_name = scenario_names.get(scenario, scenario)
    qualitative_desc = scenario_qualitative.get(scenario, "")

    # Step 1️⃣: 기존 Z-Score 계산 (정량)
    original_z_score = _calculate_z_score_from_financial_data(financial_data)

    # Step 2️⃣: 충격 계수 적용
    shocked_metrics = {}
    for key, value in financial_data.items():
        if key in shocks and value is not None:
            shocked_metrics[key] = value * shocks[key]
        else:
            shocked_metrics[key] = value

    # Step 3️⃣: 충격 후 Z-Score 계산 (정량)
    shocked_z_score = _calculate_z_score_from_financial_data(shocked_metrics)

    # Step 4️⃣: 정성 리스크 점수 계산
    qualitative_score = _calculate_qualitative_risk_score(scenario)

    # Step 5️⃣: 하이브리드 최종 점수 (정량 80% + 정성 20%)
    # Z-Score를 0-100 범위로 정규화 (역변환: 높을수록 위험)
    original_normalized = (4 - original_z_score) * 25  # 0-100
    shocked_normalized = (4 - shocked_z_score) * 25     # 0-100

    # 정성 점수도 0-100 범위로 정규화 (0-30 → 0-100)
    qualitative_normalized = (qualitative_score / 30) * 100

    # 하이브리드 점수 = 정량 지표(80%) + 정성 가중(20%)
    hybrid_score_original = original_normalized * 0.8 + qualitative_normalized * 0.2
    hybrid_score_shocked = shocked_normalized * 0.8 + qualitative_normalized * 0.2

    # 변화율 계산
    if hybrid_score_original > 0:
        change_percentage = ((hybrid_score_shocked - hybrid_score_original) / hybrid_score_original) * 100
    else:
        change_percentage = 0

    # Step 6️⃣: 하이브리드 점수를 다시 Z-Score 척도로 변환 (회복력 판정용)
    # 하이브리드 점수 0 → Z 4.0 / 100 → Z 0.0
    hybrid_z_score = 4 - (hybrid_score_shocked / 25)

    # Resilience 판정 (Z-Score 임계치 유지)
    if hybrid_z_score > 2.99:
        resilience = "견딜 수 있음"
    elif hybrid_z_score > 1.81:
        resilience = "위험"
    else:
        resilience = "심각"

    # Step 7️⃣: 투자 보고서 형식의 통합 결과 문단
    corp_name = "해당 기업"  # 추후 session_state에서 받음
    debt_impact = round((shocked_metrics.get('debt_ratio', financial_data.get('debt_ratio', 100)) - financial_data.get('debt_ratio', 100)) / financial_data.get('debt_ratio', 100) * 100, 1)

    narrative_result = (
        f"시뮬레이션 결과, {scenario_name} 발생 시 기업의 부채비율은 기존 대비 "
        f"{debt_impact:+.1f}% 증가하며 정량 재무 위험도가 크게 상승합니다. "
        f"특히 소비재 산업 특성상 정성 가중치가 높게 작용하여, "
        f"DART 주석 내 【{qualitative_desc}】 위험이 현실화될 경우 "
        f"충격 후 종합 점수는 기존 {hybrid_score_original:.1f}에서 {hybrid_score_shocked:.1f}로 급감합니다. "
        f"최종 회복력 등급은 '【{resilience}】' 단계로 판정되며, "
        f"기업은 즉각적인 가이드라인 수립이 권고됩니다."
    )

    # Step 8️⃣: 기업 맞춤형 Action Plan 생성
    action_plan = _generate_action_plan(financial_data, scenario, resilience)

    return {
        "scenario": scenario,
        "scenario_name": scenario_name,
        "scenario_description": qualitative_desc,
        "original_z_score": round(original_z_score, 2),
        "qualitative_score": qualitative_score,
        "shocked_z_score": round(shocked_z_score, 2),
        "hybrid_score_original": round(hybrid_score_original, 1),
        "hybrid_score_shocked": round(hybrid_score_shocked, 1),
        "resilience": resilience,
        "change_percentage": round(change_percentage, 1),
        "narrative_result": narrative_result,
        "action_plan": action_plan
    }
