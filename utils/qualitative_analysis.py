# -*- coding: utf-8 -*-
"""
정성적 리스크 분석 모듈
Claude LLM을 활용한 경영진 설명, 이해관계자 검증, 리스크 카테고리 추출
"""

from typing import Optional, Dict, Any, Tuple
from langchain_anthropic import ChatAnthropic


def management_explanations(corp_name: str, analysis: Dict, notes: str, llm: ChatAnthropic) -> str:
    """
    경영진 관점에서 재무 건전성을 설명하는 텍스트를 Claude LLM으로 생성합니다.

    Args:
        corp_name: 기업명
        analysis: 정량 분석 결과 dict (from financial_rule_engine)
            {
                "financial_risk_score": float,
                "risk_level": str,
                "component_scores": dict,
                ...
            }
        notes: 재무제표 주석 텍스트 (from extract_notes)
        llm: ChatAnthropic LLM 인스턴스

    Returns:
        경영진 관점의 설명 텍스트
    """
    prompt = f"""당신은 {corp_name}의 경영진 대변인으로, 재무 투명성 및 전략적 의사결정을 설명합니다.

【정량 분석 결과】
- 종합 위험도: {analysis.get('financial_risk_score', 'N/A')}/100
- 위험 수준: {analysis.get('risk_level', 'N/A')}
- 세부 지표: {str(analysis.get('component_scores', {}))}

【재무제표 주석 발췌】
{notes[:2000] if notes else "주석 없음"}

【설명 내용】
국제회계기준(K-IFRS)에 따른 당사의 재무 보고를 설명드립니다.

1. **재무 건전성 입증**
   - 정량 분석 결과의 세부 지표를 근거로 당사의 체계적 재무관리를 설명하십시오.
   - 부채비율, 유동비율, 현금흐름 관련 객관적 지표를 명시하십시오.

2. **전략적 자산 취득의 정당화**
   - 주석에서 언급된 무형자산, 종속기업 투자, 사업을 미래 성장 동력으로 설명하십시오.
   - K-IFRS 회계기준에 따른 보수적 처리 현황을 강조하십시오.

3. **리스크 관리 현황**
   - 당사의 선제적 리스크 관리 체계를 설명하십시오.
   - 회계 투명성 및 기업지배구조 개선 현황을 소명하십시오.
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"재무 설명 생성 중 오류가 발생했습니다: {str(e)}"


def stakeholder_caveats(corp_name: str, mgmt_response: str, notes: str, analysis: Dict, llm: ChatAnthropic) -> str:
    """
    이해관계자 관점에서 재무 투명성과 숨겨진 리스크를 검증하는 Claude LLM 분석입니다.

    우발채무, 특수관계자 거래, 자산손상을 집중 분석합니다.

    Args:
        corp_name: 기업명
        mgmt_response: 경영진 설명 텍스트 (from management_explanations)
        notes: 재무제표 주석 텍스트 (from extract_notes)
        analysis: 정량 분석 결과 dict
        llm: ChatAnthropic LLM 인스턴스

    Returns:
        이해관계자 관점의 검증 텍스트
    """
    prompt = f"""당신은 기업지배구조 및 회계감시 전문가로, 국제 투자자의 의뢰로 {corp_name}의 재무 투명성을 검증합니다.

【정량 분석 결과】
- 종합 위험도: {analysis.get('financial_risk_score', 'N/A')}/100
- 위험 수준: {analysis.get('risk_level', 'N/A')}

【경영진의 설명】
{mgmt_response[:1500]}

【재무제표 주석】
{notes if notes else "주석 없음"}

【정성적 검증】

재무 건전성에도 불구하고, 주석에 대한 정밀 분석을 수행합니다.

**① 우발채무 및 계류 중인 소송**
   - 주석에서 진행 중인 소송, 분쟁, 법적 리스크를 추적하십시오.
   - 미결제 우발채무 규모와 해결 시점의 불확실성을 지적하십시오.
   - 발견 내용: 구체적으로 인용하십시오.

**② 특수관계자 거래 및 자금 이동**
   - 주석에서 지배주주, 경영진, 계열사 간의 자금 이동을 추적하십시오.
   - 부당한 거래 가격 책정, 담보 제공, 보증 약정의 투명성을 지적하십시오.
   - 발견 내용: 구체적으로 인용하십시오.

**③ 자산손상차손 및 투자 손실**
   - 주석에서 M&A 자산, 무형자산, 투자 관련 손상을 추적하십시오.
   - 과거 인수 기업의 영업 부진, 손상 인식 규모를 분석하십시오.
   - 발견 내용: 구체적으로 인용하십시오.

【최종 평가】
투자자 관점에서:
- 제시된 위험 요소가 얼마나 심각한가?
- 추가 공시 또는 감시가 필요한가?
- 투자 진행 여부에 대한 평가를 명시하십시오.
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"정성적 검증 생성 중 오류가 발생했습니다: {str(e)}"


def extract_risk_categories(caveats_text: str) -> Dict:
    """
    Claude 정성 분석 텍스트에서 리스크 항목을 추출합니다.

    3가지 카테고리로 분류:
    - 우발채무 & 소송
    - 특수관계자 거래
    - 자산손상 & 투자손실

    Args:
        caveats_text: stakeholder_caveats() 결과 텍스트

    Returns:
        {
            "contingent_liabilities": [...],      # 우발채무 리스트
            "contingent_liabilities_details": [...],
            "related_party_transactions": [...],  # 특수관계자 거래 리스트
            "related_party_transactions_details": [...],
            "asset_impairment": [...],            # 자산손상 리스트
            "asset_impairment_details": [...],
            "investment_assessment": "",          # 최종 평가
            "contingent_count": int,
            "related_count": int,
            "asset_count": int,
            "assessment_count": int
        }
    """
    categories = {
        "contingent_liabilities": [],
        "contingent_liabilities_details": [],
        "related_party_transactions": [],
        "related_party_transactions_details": [],
        "asset_impairment": [],
        "asset_impairment_details": [],
        "investment_assessment": "",
    }

    if not caveats_text or len(caveats_text) < 50:
        return categories

    text = caveats_text

    # === 섹션별 텍스트 분할 ===
    sections = {
        "contingent": [],
        "related": [],
        "asset": []
    }

    # 우발채무 섹션 추출
    if '우발' in text or '소송' in text:
        lines = text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['우발', '소송', '분쟁', '법적', '청구']):
                sections["contingent"].append(line.strip())

    # 특수관계자 섹션 추출
    if '특수' in text or '관계자' in text or '계열' in text:
        lines = text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['특수', '관계자', '계열', '지배', '자금']):
                sections["related"].append(line.strip())

    # 자산손상 섹션 추출
    if '손상' in text or '투자손실' in text or 'M&A' in text:
        lines = text.split('\n')
        for line in lines:
            if any(kw in line for kw in ['손상', '투자손실', 'M&A', '투자', '무형자산']):
                sections["asset"].append(line.strip())

    # === 항목 개수 계산 ===
    contingent_count = 1 if sections["contingent"] else 0
    related_count = 1 if sections["related"] else 0
    asset_count = 1 if sections["asset"] else 0
    has_assessment = 1 if ('권고' in text or '투자' in text or '평가' in text) else 0

    # === 결과 저장 ===
    if sections["contingent"]:
        categories["contingent_liabilities"] = ['\n'.join(sections["contingent"])[:100]]
        categories["contingent_liabilities_details"] = ['\n'.join(sections["contingent"])]

    if sections["related"]:
        categories["related_party_transactions"] = ['\n'.join(sections["related"])[:100]]
        categories["related_party_transactions_details"] = ['\n'.join(sections["related"])]

    if sections["asset"]:
        categories["asset_impairment"] = ['\n'.join(sections["asset"])[:100]]
        categories["asset_impairment_details"] = ['\n'.join(sections["asset"])]

    # 투자 평가
    if has_assessment:
        for line in text.split('\n'):
            if any(kw in line for kw in ['권고', '투자', '평가', '결론']):
                categories["investment_assessment"] = line.strip()[:200]
                break

    # 명시적 항목 개수 저장
    categories["contingent_count"] = contingent_count
    categories["related_count"] = related_count
    categories["asset_count"] = asset_count
    categories["assessment_count"] = has_assessment

    return categories


def _generate_qualitative_rationale(
    con_count: int,
    rel_count: int,
    asset_count: int,
    has_assessment: int,
    risk_categories: Dict
) -> str:
    """
    정성 점수의 정당성을 구조화된 형식으로 설명합니다.

    각 카테고리별로 "구체적 근거 → 평가 → 점수 반영" 구조를 명확하게 표시합니다.

    Args:
        con_count: 우발채무 항목 개수
        rel_count: 특수관계자 거래 항목 개수
        asset_count: 자산손상 항목 개수
        has_assessment: 최종 평가 여부 (0 또는 1)
        risk_categories: extract_risk_categories() 결과

    Returns:
        점수 정당성 설명 텍스트
    """
    rationale_parts = []

    # === 우발채무 & 소송 ===
    con_score = min(con_count * 15, 45)
    if con_count > 0:
        con_details = risk_categories.get("contingent_liabilities_details", [])
        con_text = con_details[0] if con_details else f"우발채무 {con_count}건이 발견되었습니다."

        rationale_parts.append(
            f"**【우발채무 & 소송】**\n\n"
            f"📌 구체적 근거:\n"
            f"{con_text[:200]}\n\n"
            f"📌 평가:\n"
            f"공시 주석에서 확인된 소송 사건 및 우발채무는 "
            f"향후 재무 상황에 영향을 미칠 수 있는 법적 리스크를 나타냅니다.\n\n"
            f"📌 점수 반영:\n"
            f"위 사항에 대해 우발채무 카테고리에 {con_score:.0f}점을 부여합니다.\n"
        )
    else:
        rationale_parts.append(
            f"**【우발채무 & 소송】**\n\n"
            f"📌 평가:\n"
            f"공시 주석에서 중대한 소송 사건이나 우발채무가 발견되지 않았습니다.\n"
            f"따라서 법적 분쟁 리스크는 낮은 것으로 평가됩니다.\n\n"
            f"📌 점수 반영:\n"
            f"우발채무 카테고리에 0점을 부여합니다.\n"
        )

    # === 특수관계자거래 ===
    rel_score = min(rel_count * 20, 40)
    if rel_count > 0:
        rel_details = risk_categories.get("related_party_transactions_details", [])
        rel_text = rel_details[0] if rel_details else f"특수관계자거래 {rel_count}건이 발견되었습니다."

        rationale_parts.append(
            f"**【특수관계자거래】**\n\n"
            f"📌 구체적 근거:\n"
            f"{rel_text[:200]}\n\n"
            f"📌 평가:\n"
            f"지배주주 및 관계회사와의 거래는 경영진의 편의적 의사결정이나 "
            f"자산 이전의 신호가 될 수 있습니다. 공시의 투명성과 공정성을 검증하는 것이 중요합니다.\n\n"
            f"📌 점수 반영:\n"
            f"위 사항에 대해 특수관계자거래 카테고리에 {rel_score:.0f}점을 부여합니다.\n"
        )
    else:
        rationale_parts.append(
            f"**【특수관계자거래】**\n\n"
            f"📌 평가:\n"
            f"공시 주석에서 부당한 특수관계자거래가 발견되지 않았습니다.\n"
            f"지배주주 및 관계회사와의 거래는 통상적인 수준으로 평가됩니다.\n\n"
            f"📌 점수 반영:\n"
            f"특수관계자거래 카테고리에 0점을 부여합니다.\n"
        )

    # === 자산손상 & 투자손실 ===
    asset_score = min(asset_count * 20, 40)
    if asset_count > 0:
        asset_details = risk_categories.get("asset_impairment_details", [])
        asset_text = asset_details[0] if asset_details else f"자산손상 {asset_count}건이 발견되었습니다."

        rationale_parts.append(
            f"**【자산손상 & 투자손실】**\n\n"
            f"📌 구체적 근거:\n"
            f"{asset_text[:200]}\n\n"
            f"📌 평가:\n"
            f"종속기업 투자, 무형자산, M&A 자산 등에서 손상이 인식되었습니다. "
            f"이는 과거 전략적 투자가 기대 수익을 창출하지 못했음을 의미합니다.\n\n"
            f"📌 점수 반영:\n"
            f"위 사항에 대해 자산손상 카테고리에 {asset_score:.0f}점을 부여합니다.\n"
        )
    else:
        rationale_parts.append(
            f"**【자산손상 & 투자손실】**\n\n"
            f"📌 평가:\n"
            f"공시 주석에서 중대한 자산손상이나 투자손실이 발견되지 않았습니다.\n"
            f"기업의 자산은 합리적인 가치로 평가되고 있습니다.\n\n"
            f"📌 점수 반영:\n"
            f"자산손상 카테고리에 0점을 부여합니다.\n"
        )

    # === 최종평가 ===
    assess_score = 25 if has_assessment else 0
    if has_assessment:
        rationale_parts.append(
            f"**【최종평가】**\n\n"
            f"📌 평가:\n"
            f"공시 주석에 대한 종합 검증 결과, 기업의 재무 투명성과 지배구조는 "
            f"합리적 수준으로 평가됩니다.\n\n"
            f"📌 점수 반영:\n"
            f"최종 정성평가에 {assess_score:.0f}점을 부여합니다.\n"
        )

    # === 종합 결론 ===
    total = con_score + rel_score + asset_score + assess_score
    total = min(total, 100)

    if total > 70:
        risk_level = "**고위험** 🔴"
        interpretation = "공시 주석에서 발견된 리스크 항목들이 상당하므로, 추가 실사가 필요합니다."
    elif total > 50:
        risk_level = "**중위험** 🟠"
        interpretation = "공시 주석에서 일부 리스크 항목이 식별되었으므로, 주의 깊은 모니터링이 필요합니다."
    else:
        risk_level = "**저위험** 🟢"
        interpretation = "공시 주석상 정성 리스크는 낮은 수준으로 평가됩니다."

    rationale_parts.append(
        f"\n**【종합 분석 결론】**\n\n"
        f"📊 정성 리스크 총점: **{total:.0f}/100점** ({risk_level})\n\n"
        f"📋 해석:\n"
        f"{interpretation}"
    )

    return "\n".join(rationale_parts)


def extract_qualitative_risk_score(risk_categories: Dict) -> Dict:
    """
    extract_risk_categories() 결과에서 정성 위험도 점수를 계산합니다.

    점수 계산 기준:
    - 우발채무: 항목당 15점 (최대 45점)
    - 특수관계자거래: 항목당 20점 (최대 40점)
    - 자산손상: 항목당 20점 (최대 40점)
    - 투자 평가: 25점 (있으면 추가)
    - 총 최대 100점

    Args:
        risk_categories: extract_risk_categories() 결과

    Returns:
        {
            "qualitative_risk_score": float,           # 0-100 점수
            "risk_count": int,                         # 리스크 카테고리 개수
            "risk_breakdown": {                        # 카테고리별 항목 개수
                "contingent_liabilities": int,
                "related_party_transactions": int,
                "asset_impairment": int,
                "investment_assessment": int
            },
            "scoring_details": {
                "contingent_score": float,
                "related_score": float,
                "asset_score": float,
                "assessment_score": float,
                "rationale": str
            }
        }
    """
    risk_breakdown = {}
    categories_with_risk = 0
    qualitative_risk_score = 0

    # 항목 개수 계산
    contingent_count = risk_categories.get("contingent_count") or len(
        risk_categories.get("contingent_liabilities_details", [])
    )
    related_count = risk_categories.get("related_count") or len(
        risk_categories.get("related_party_transactions_details", [])
    )
    asset_count = risk_categories.get("asset_count") or len(
        risk_categories.get("asset_impairment_details", [])
    )

    assessment_text = risk_categories.get("investment_assessment", "") or risk_categories.get("final_recommendation", "")
    has_assessment = 1 if (assessment_text and len(assessment_text.strip()) > 0) else 0

    # === 우발채무 점수 계산 ===
    risk_breakdown["contingent_liabilities"] = contingent_count
    contingent_score = min(contingent_count * 15, 45)
    qualitative_risk_score += contingent_score
    if contingent_count > 0:
        categories_with_risk += 1

    # === 특수관계자거래 점수 계산 ===
    risk_breakdown["related_party_transactions"] = related_count
    related_score = min(related_count * 20, 40)
    qualitative_risk_score += related_score
    if related_count > 0:
        categories_with_risk += 1

    # === 자산손상 점수 계산 ===
    risk_breakdown["asset_impairment"] = asset_count
    asset_score = min(asset_count * 20, 40)
    qualitative_risk_score += asset_score
    if asset_count > 0:
        categories_with_risk += 1

    # === 투자 평가 점수 계산 ===
    risk_breakdown["investment_assessment"] = has_assessment
    if has_assessment > 0:
        qualitative_risk_score += 25
        categories_with_risk += 1

    # 최대 100점 제한
    qualitative_risk_score = min(qualitative_risk_score, 100)

    # 점수 정당성 설명 생성
    scoring_rationale = _generate_qualitative_rationale(
        contingent_count, related_count, asset_count, has_assessment,
        risk_categories
    )

    return {
        "qualitative_risk_score": round(qualitative_risk_score, 1),
        "risk_count": categories_with_risk,
        "risk_breakdown": risk_breakdown,
        "scoring_details": {
            "contingent_score": round(min(contingent_count * 15, 45), 1),
            "related_score": round(min(related_count * 20, 40), 1),
            "asset_score": round(min(asset_count * 20, 40), 1),
            "assessment_score": 25 if has_assessment else 0,
            "rationale": scoring_rationale
        }
    }
