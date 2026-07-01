# -*- coding: utf-8 -*-
"""
McKinsey/BCG 스타일 Executive Summary 보고서 PDF 생성
- 풍부한 서술형 본문
- 고급 테이블 스타일
- Header/Footer + 페이지 번호
- 지표 카드 박스
- Deep Green/Light Green 테마
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, PageTemplate, Frame
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os


def _setup_korean_font():
    """한글 폰트 설정"""
    try:
        font_path = r"C:\Windows\Fonts\malgun.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
            return 'MalgunGothic'
    except Exception:
        pass
    return 'Helvetica'


class PageNumCanvas:
    """페이지 번호 Canvas"""
    def __init__(self, doc, font_name):
        self.doc = doc
        self.font_name = font_name

    def __call__(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(self.font_name, 8)
        canvas.setFillColor(colors.HexColor('#999999'))
        canvas.drawRightString(19*cm, 1*cm, f"Page {doc.page}")
        canvas.restoreState()


def generate_risk_report_pdf(report_data: dict) -> bytes:
    """
    McKinsey 스타일 Executive Summary 보고서 생성
    """

    font_name = _setup_korean_font()

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=1.2*cm,
        leftMargin=1.2*cm,
        topMargin=1.8*cm,
        bottomMargin=1.8*cm
    )

    # ========================================================================
    # 스타일 정의
    # ========================================================================
    styles = getSampleStyleSheet()

    # 색상 상수
    DEEP_GREEN = colors.HexColor('#1E4620')
    LIGHT_GREEN = colors.HexColor('#F4F9F4')
    GRAY_TEXT = colors.HexColor('#4A4A4A')

    # 메인 타이틀
    main_title = ParagraphStyle(
        'MainTitle',
        fontName=font_name,
        fontSize=26,
        leading=39,
        textColor=DEEP_GREEN,
        spaceAfter=6,
        alignment=TA_CENTER,
        bold=True,
        wordWrap='CJK'
    )

    # 서브 타이틀
    sub_title = ParagraphStyle(
        'SubTitle',
        fontName=font_name,
        fontSize=14,
        leading=21,
        textColor=DEEP_GREEN,
        spaceAfter=20,
        alignment=TA_CENTER,
        bold=True,
        wordWrap='CJK'
    )

    # 섹션 헤더
    section_header = ParagraphStyle(
        'SectionHeader',
        fontName=font_name,
        fontSize=12,
        leading=18,
        textColor=colors.white,
        spaceAfter=10,
        spaceBefore=12,
        bold=True,
        leftIndent=8,
        wordWrap='CJK'
    )

    # 본문 (풍부한 내용)
    body_text = ParagraphStyle(
        'BodyText',
        fontName=font_name,
        fontSize=10,
        leading=16,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        textColor=GRAY_TEXT,
        leftIndent=6,
        rightIndent=6,
        wordWrap='CJK'
    )

    # 강조 텍스트
    highlight_text = ParagraphStyle(
        'HighlightText',
        fontName=font_name,
        fontSize=10,
        leading=16,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        textColor=DEEP_GREEN,
        bold=True,
        leftIndent=6,
        rightIndent=6,
        wordWrap='CJK'
    )

    # 테이블 셀
    table_cell = ParagraphStyle(
        'TableCell',
        fontName=font_name,
        fontSize=9,
        leading=14,
        alignment=TA_CENTER,
        wordWrap='CJK'
    )

    # 메타
    meta_text = ParagraphStyle(
        'MetaText',
        fontName=font_name,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor('#888888'),
        wordWrap='CJK'
    )

    # PDF 컨텐츠
    elements = []

    # ========================================================================
    # [표지 페이지]
    # ========================================================================
    elements.append(Spacer(1, 2*cm))

    elements.append(Paragraph("【Executive Summary】", main_title))
    elements.append(Paragraph("기업 종합 리스크 진단 보고서", sub_title))

    elements.append(Spacer(1, 1*cm))

    # 메타 정보
    corp_name = report_data.get('corp_name', '기업명')
    report_date = report_data.get('report_date', '')

    meta_info = f"""
    <b>분석 대상:</b> {corp_name}<br/>
    <b>분석 일시:</b> {report_date}<br/>
    <b>분석 유형:</b> AI 기반 정량·정성 복합 위험도 분석<br/>
    """

    elements.append(Paragraph(meta_info, meta_text))

    elements.append(Spacer(1, 2*cm))

    # ========================================================================
    # [Executive Overview - 종합 판정]
    # ========================================================================
    elements.append(PageBreak())

    # 섹션 헤더
    header_table = Table([["1. EXECUTIVE OVERVIEW"]])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DEEP_GREEN),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOLD', (0, 0), (-1, -1), True),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, DEEP_GREEN),
    ]))
    elements.append(header_table)

    elements.append(Spacer(1, 0.3*cm))

    # 종합 위험도 카드 (박스 스타일)
    final_risk_score = report_data.get('final_risk_score', 0)
    final_risk_level = report_data.get('final_risk_level', '미판정')
    final_risk_grade = report_data.get('final_risk_grade', '미판정')

    # ✅ 대시보드와 일치하는 레이블 체계: "저위험"/"중위험"/"고위험"
    risk_color_map = {
        '저위험': colors.HexColor('#27ae60'),      # 🟢 Green
        '중위험': colors.HexColor('#f39c12'),      # 🟡 Orange
        '고위험': colors.HexColor('#e74c3c')       # 🔴 Red
    }
    risk_color = risk_color_map.get(final_risk_level, colors.grey)

    risk_card_data = [
        ["최종 위험 등급", "최종 위험 점수", "위험 판정"],
        [
            Paragraph(f"<b><font color='{risk_color.hexval()}'>{final_risk_level}</font></b>", table_cell),
            Paragraph(f"<b>{final_risk_score:.1f}점</b>", table_cell),
            Paragraph(f"<b>{final_risk_grade}</b>", table_cell),
        ]
    ]

    risk_card = Table(risk_card_data, colWidths=[4*cm, 4*cm, 5*cm])
    risk_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_GREEN),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LINEBELOW', (0, 0), (-1, 0), 1, DEEP_GREEN),
        ('LINEBELOW', (0, 1), (-1, 1), 1, colors.HexColor('#d0d0d0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(risk_card)

    elements.append(Spacer(1, 0.6*cm))

    # 종합 평가 텍스트
    overview_text = f"""
    본 보고서는 AI 기반 정량·정성 복합 분석을 통해 {corp_name}의 재무 건전성과 위험 수준을
    종합적으로 평가합니다. 정량 분석(매출 질, 유동성, 부채 비율)과 정성 분석(DART 주석 기반
    리스크 카테고리)을 통합하여 도출한 최종 위험 등급은 <b>{final_risk_level}</b>이며,
    위험 점수는 <b>{final_risk_score:.1f}점</b>입니다.
    """
    elements.append(Paragraph(overview_text, body_text))

    elements.append(Spacer(1, 0.8*cm))

    # ========================================================================
    # [정량 재무 분석]
    # ========================================================================
    header_table = Table([["2. 정량 재무 리스크 분석"]])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DEEP_GREEN),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOLD', (0, 0), (-1, -1), True),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, DEEP_GREEN),
    ]))
    elements.append(header_table)

    elements.append(Spacer(1, 0.3*cm))

    # 재무 지표 테이블
    component_scores = report_data.get('component_scores', {})
    current_ratio = report_data.get('current_ratio', 0)
    debt_ratio = report_data.get('debt_ratio', 0)

    financial_data = [
        ["평가 항목", "점수 (0~100)", "배중도", "상태"],
        [
            Paragraph("매출 질 지표 (Revenue Quality)", table_cell),
            Paragraph(f"{component_scores.get('revenue_quality', 0):.0f}", table_cell),
            Paragraph("40%", table_cell),
            Paragraph("정상" if component_scores.get('revenue_quality', 100) < 40 else "주의", table_cell),
        ],
        [
            Paragraph("유동성 스트레스 (Liquidity Stress)", table_cell),
            Paragraph(f"{component_scores.get('liquidity_stress', 0):.0f}", table_cell),
            Paragraph("35%", table_cell),
            Paragraph("정상" if component_scores.get('liquidity_stress', 100) < 40 else "주의", table_cell),
        ],
        [
            Paragraph("부채 위험 지수 (Leverage Risk)", table_cell),
            Paragraph(f"{component_scores.get('leverage_risk', 0):.0f}", table_cell),
            Paragraph("25%", table_cell),
            Paragraph("정상" if component_scores.get('leverage_risk', 100) < 40 else "주의", table_cell),
        ],
    ]

    financial_table = Table(financial_data, colWidths=[4.2*cm, 2.5*cm, 2*cm, 2.3*cm])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5F36')),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_GREEN),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOLD', (0, 0), (-1, 0), True),
        ('LINEBELOW', (0, 0), (-1, 0), 1, DEEP_GREEN),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(financial_table)

    elements.append(Spacer(1, 0.4*cm))

    # 주요 재무지표
    key_metrics_text = f"""
    <b>주요 재무 지표:</b> 유동비율 {current_ratio:.1f}% | 부채비율 {debt_ratio:.1f}%<br/>
    <b>평가:</b> 유동비율이 150% 이상이면 단기 지급 능력이 양호하고, 부채비율이 100% 이하이면
    재무 레버리지가 안전한 범주로 판단됩니다. 현재 {corp_name}의 유동비율과 부채비율을
    종합적으로 평가할 때, 기업의 단기 및 장기 지급 능력은 산업 평균 대비 양호한 수준을 유지하고 있습니다.
    """
    elements.append(Paragraph(key_metrics_text, body_text))

    elements.append(Spacer(1, 0.8*cm))

    # ========================================================================
    # [정성 리스크 분석]
    # ========================================================================
    header_table = Table([["3. DART 주석 기반 정성 리스크 분석"]])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DEEP_GREEN),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOLD', (0, 0), (-1, -1), True),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, DEEP_GREEN),
    ]))
    elements.append(header_table)

    elements.append(Spacer(1, 0.3*cm))

    # 정성 리스크
    risk_categories = report_data.get('risk_categories', {})
    qualitative_score = report_data.get('qualitative_risk_score', 0)

    if risk_categories:
        category_text = "<b>감지된 주요 리스크 카테고리:</b><br/>"
        for idx, (category, count) in enumerate(risk_categories.items(), 1):
            category_text += f"&nbsp;&nbsp;• {category}: {count}건<br/>"
    else:
        category_text = "<b>감지된 주요 리스크 카테고리:</b><br/>&nbsp;&nbsp;• 특이 사항 없음"

    elements.append(Paragraph(category_text, body_text))

    elements.append(Spacer(1, 0.2*cm))

    qual_text = f"""
    <b>정성 위험도 종합 점수:</b> {qualitative_score:.1f}/100<br/>
    DART 재무제표 주석 분석을 통해 감지된 정성적 위험 요소들을 종합적으로 평가하면,
    기업의 정성 위험도는 양호한 수준을 유지하고 있습니다. 정기적인 모니터링을 통해
    신규 위험 요소 발생 여부를 추적할 필요가 있습니다.
    """
    elements.append(Paragraph(qual_text, body_text))

    # ========================================================================
    # [시나리오 분석 & 맞춤형 전략]
    # ========================================================================
    scenario_result = report_data.get('scenario_result')
    if scenario_result:
        elements.append(Spacer(1, 0.8*cm))

        header_table = Table([["4. 위기 시나리오 스트레스 테스트 및 전략"]])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), DEEP_GREEN),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BOLD', (0, 0), (-1, -1), True),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 1.5, DEEP_GREEN),
        ]))
        elements.append(header_table)

        elements.append(Spacer(1, 0.3*cm))

        scenario_name = scenario_result.get('scenario_name', '미선택')
        original_z = scenario_result.get('original_z_score', 0)
        shocked_z = scenario_result.get('shocked_z_score', 0)
        resilience = scenario_result.get('resilience', '미판정')

        # 시나리오 개요
        scenario_text = f"""
        <b>선택된 시나리오:</b> {scenario_name}<br/>
        <b>회복력 등급:</b> {resilience}<br/>
        <b>Z-Score 변동:</b> {original_z:.2f} → {shocked_z:.2f}<br/>
        """
        elements.append(Paragraph(scenario_text, body_text))

        elements.append(Spacer(1, 0.2*cm))

        # 시뮬레이션 분석 결과
        narrative = report_data.get('scenario_narrative', '')
        if narrative:
            elements.append(Paragraph(narrative, body_text))

        elements.append(Spacer(1, 0.3*cm))

        # 맞춤형 권고사항
        action_plan = report_data.get('action_plan_text', '')
        if action_plan:
            elements.append(Paragraph("<b>【기업 맞춤형 리스크 대응 전략】</b>", highlight_text))
            elements.append(Spacer(1, 0.15*cm))
            elements.append(Paragraph(action_plan.replace('\n', '<br/>'), body_text))

    # ========================================================================
    # [결론 및 면책]
    # ========================================================================
    elements.append(Spacer(1, 1*cm))

    elements.append(Paragraph("결론 및 면책 조항", section_header))

    conclusion_text = f"""
    본 분석은 공개된 DART 재무제표 및 공개 정보에 기반한 AI 자동화 분석입니다. 분석 결과는
    정보 제공 목적이며, 투자 또는 경영 의사결정의 유일한 근거로 활용되어서는 안 됩니다.
    기업의 재무 상황은 지속적으로 변화하므로, 정기적인 업데이트 및 전문가의 자문을 권장합니다.
    """
    elements.append(Paragraph(conclusion_text, body_text))

    # ========================================================================
    # PDF 생성
    # ========================================================================
    try:
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    except Exception as e:
        print(f"PDF 생성 오류: {e}")
        raise
