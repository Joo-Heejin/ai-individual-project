# -*- coding: utf-8 -*-
"""
정성 가중치 민감도 분석
최종 점수 = (정량 × (1-w)) + (정성 × w) 에서
w(정성 가중치)가 변할 때 최종 등급의 변화를 분석합니다.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 아모레퍼시픽 데이터 (현황)
corp_name = "아모레퍼시픽"
financial_score = 36.7  # 정량 점수
qualitative_score = 65.0  # 정성 점수

def calculate_final_score(fin_score, qual_score, qual_weight):
    """최종 점수 = (정량 × (1-w)) + (정성 × w)"""
    fin_weight = 1 - qual_weight
    return (fin_score * fin_weight) + (qual_score * qual_weight)

def get_risk_grade(score):
    """최종 등급 판정"""
    if score > 70:
        return "고위험", "🔴"
    elif score > 50:
        return "중위험", "🟠"
    else:
        return "저위험", "🟢"

print("=" * 80)
print(f"【정성 가중치 민감도 분석】")
print(f"기업: {corp_name}")
print("=" * 80)

print(f"\n현재 상황:")
print(f"  정량 점수: {financial_score:.1f}점")
print(f"  정성 점수: {qualitative_score:.1f}점")
print(f"  현재 가중치: 정량 60% / 정성 40%")

current_final = calculate_final_score(financial_score, qualitative_score, 0.4)
current_grade, current_emoji = get_risk_grade(current_final)
print(f"  현재 최종 점수: {current_final:.1f}점 ({current_emoji} {current_grade})")

print("\n" + "=" * 80)
print("【정성 가중치 변화에 따른 최종 등급 변화】")
print("=" * 80)

# 가중치 0%부터 100%까지 변화 분석
print(f"\n{'정성가중치':<12} {'정량가중치':<12} {'최종점수':<12} {'등급':<15}")
print("-" * 80)

sensitivity_data = []
for qual_weight in range(0, 101, 10):
    fin_weight = 100 - qual_weight
    final_score = calculate_final_score(financial_score, qualitative_score, qual_weight/100)
    grade, emoji = get_risk_grade(final_score)

    print(f"{qual_weight}%{'':<9} {fin_weight}%{'':<9} {final_score:.1f}점{'':<6} {emoji} {grade}")
    sensitivity_data.append({
        'qual_weight': qual_weight,
        'final_score': final_score,
        'grade': grade,
        'emoji': emoji
    })

# 핵심 임계점 찾기
print("\n" + "=" * 80)
print("【핵심 임계점 분석】")
print("=" * 80)

# 저위험 → 중위험 임계점 (최종점수 50점)
# 50 = (36.7 × (1-w)) + (65 × w)
# 50 = 36.7 - 36.7w + 65w
# 50 - 36.7 = 28.3w
# w = (50 - 36.7) / 28.3
threshold_medium = (50 - financial_score) / (qualitative_score - financial_score)
print(f"\n✓ 저위험 → 중위험 임계점")
print(f"  정성 가중치: {threshold_medium*100:.1f}%")
print(f"  해석: 정성 가중치가 {threshold_medium*100:.1f}% 이상이면 중위험 진입")

# 중위험 → 고위험 임계점 (최종점수 70점)
threshold_high = (70 - financial_score) / (qualitative_score - financial_score)
if threshold_high <= 1.0:
    print(f"\n✓ 중위험 → 고위험 임계점")
    print(f"  정성 가중치: {threshold_high*100:.1f}%")
    print(f"  해석: 정성 가중치가 {threshold_high*100:.1f}% 이상이면 고위험 진입")
else:
    print(f"\n✗ 고위험 진입 불가능")
    print(f"  이유: 정성 가중치 100%일 때도 최종 점수 {qualitative_score:.1f}점 < 70점")

# 현재 설정 (40%)에서의 위치
print(f"\n✓ 현재 설정 (정성 40%)")
print(f"  최종 점수: {current_final:.1f}점")
print(f"  등급: {current_emoji} {current_grade}")
print(f"  저위험 경계까지의 여유: {current_final - 50:.1f}점")

# 가중치 변화 권고
print("\n" + "=" * 80)
print("【가중치 조정 권고】")
print("=" * 80)

print(f"\n현재 정성 가중치 40%는 적절한가?")
print(f"\n분석 결과:")
print(f"  • 정량 점수(36.7점)가 정성 점수(65.0점)보다 훨씬 낮음")
print(f"  • 정성이 상대적으로 부정적 신호를 더 반영하고 있음")
print(f"  • 현재 40% 가중치는 합리적 수준")

print(f"\n가중치 조정 시나리오:")
print(f"\n1️⃣ 정성 가중치 30% (보수적)")
final_30 = calculate_final_score(financial_score, qualitative_score, 0.3)
grade_30, emoji_30 = get_risk_grade(final_30)
print(f"   최종 점수: {final_30:.1f}점 ({emoji_30} {grade_30})")
print(f"   효과: 정성 리스크의 영향도 감소")

print(f"\n2️⃣ 정성 가중치 40% (현재 권고)")
print(f"   최종 점수: {current_final:.1f}점 ({current_emoji} {current_grade})")
print(f"   효과: 정량과 정성의 균형잡힌 평가")

print(f"\n3️⃣ 정성 가중치 50% (적극적)")
final_50 = calculate_final_score(financial_score, qualitative_score, 0.5)
grade_50, emoji_50 = get_risk_grade(final_50)
print(f"   최종 점수: {final_50:.1f}점 ({emoji_50} {grade_50})")
print(f"   효과: 정성 리스크의 영향도 증대")

print("\n" + "=" * 80)
print("【최종 결론】")
print("=" * 80)

print(f"""
현재 정성 가중치 40%에서:
  ✓ 최종 점수: {current_final:.1f}점 (저위험)
  ✓ 신용등급: A1 수준 유지
  ✓ 안정성 평가: 높음

가중치 변경 전에 고려할 사항:
  1. 정성 점수(65점)는 중간 수준 리스크를 반영
  2. 정량 점수(36.7점)는 양호한 수준
  3. 현재 60:40 비중이 두 지표의 균형을 반영

권고:
  ✓ 현재 40% 가중치 유지 권고
  ✓ 정성 리스크 모니터링 강화
  ✓ 정량 지표 개선에 집중
""")

print("=" * 80)
