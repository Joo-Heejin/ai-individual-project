# -*- coding: utf-8 -*-
"""
Streamlit UI 공통 헬퍼 모듈
페이지 설정, CSS 스타일, 세션 상태 초기화 등을 제공합니다.
"""

import streamlit as st
import os
from typing import Dict, Optional


def setup_page_config() -> None:
    """
    Streamlit 페이지 기본 설정을 초기화합니다.
    이 함수는 app.py (진입점)에서 가장 먼저 호출되어야 합니다.
    """
    st.set_page_config(
        page_title="Enterprise Risk Detection System",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def apply_custom_css() -> None:
    """
    통일된 커스텀 CSS 스타일을 적용합니다.
    모든 페이지에서 일관된 디자인을 유지하기 위해 호출합니다.
    """
    st.markdown("""
    <style>
        /* 사이드바 'app' 메뉴 숨기기 */
        [data-testid="stSidebarNav"] li:first-child {
            display: none !important;
        }

        /* 사이드바 페이지 메뉴 글씨 크기 확대 */
        [data-testid="stSidebarNav"] span {
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
        }

        /* 사이드바 메뉴 아이템 간격 */
        [data-testid="stSidebarNav"] li {
            padding: 8px 0 !important;
        }

        /* 사이드바 토글 버튼 완전 제거 */
        button[aria-label="Collapse sidebar"] {
            display: none !important;
        }

        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');

        * {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        input {
            font-size: 1.5em !important;
            letter-spacing: 0.5px !important;
        }

        button {
            font-size: 1.5em !important;
            font-weight: 600 !important;
        }

        body {
            background: linear-gradient(135deg, #f0f7f2 0%, #e8f5e9 100%);
            color: #1b3a2a;
        }

        .deco-blob-1 {
            position: fixed;
            top: -50px;
            right: -100px;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(45, 106, 79, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            filter: blur(60px);
            z-index: -1;
            pointer-events: none;
        }

        .deco-blob-2 {
            position: fixed;
            bottom: -100px;
            left: -100px;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(27, 67, 50, 0.06) 0%, transparent 70%);
            border-radius: 50%;
            filter: blur(80px);
            z-index: -1;
            pointer-events: none;
        }

        [data-testid="stSidebar"] {
            background: white !important;
            backdrop-filter: none !important;
            border-right: 1px solid #e0e0e0;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid #a5d6a7;
        }

        .stTabs [aria-selected="true"] {
            border-bottom: 3px solid #1b4332 !important;
            color: #1b4332 !important;
            font-weight: 600;
        }

        .stTabs [aria-selected="false"] {
            color: #558b63;
            font-weight: 500;
        }

        .analysis-card {
            background: rgba(255, 255, 255, 0.85);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #c8e6c9;
            margin: 16px 0;
            box-shadow: 0 4px 16px rgba(27, 67, 50, 0.08);
            line-height: 1.9;
            backdrop-filter: blur(10px);
        }

        .section-header {
            border-left: 4px solid #1b4332;
            padding-left: 16px;
            margin: 24px 0 16px 0;
            font-weight: 600;
            color: #1b4332;
            font-size: 1.1em;
        }

        .metric-card {
            background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
            box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2);
        }

        [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
            border-radius: 16px;
        }

        .risk-high {
            color: #c41c3b;
            font-weight: 700;
        }

        .risk-normal {
            color: #2e7d32;
            font-weight: 700;
        }

        .risk-caution {
            color: #f57c00;
            font-weight: 700;
        }

        [data-testid="stExpander"] {
            border: 1px solid #a5d6a7 !important;
            border-radius: 12px !important;
            background: rgba(232, 245, 233, 0.3) !important;
            padding: 16px !important;
        }

        [data-testid="stExpander"] summary {
            font-weight: 600 !important;
            font-size: 1.05em !important;
            line-height: 1.8 !important;
            padding: 12px 0 !important;
            word-break: break-word !important;
        }

        [data-testid="stExpander"] p {
            margin: 12px 0 !important;
            line-height: 1.8 !important;
            font-size: 1.01em !important;
        }

        [data-testid="stExpander"] ul {
            margin: 12px 0 !important;
            padding-left: 24px !important;
        }

        [data-testid="stExpander"] li {
            margin: 8px 0 !important;
            line-height: 1.8 !important;
            font-size: 1.01em !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px 20px;
            font-size: 1.5em !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
        }

        .stTextInput > div > div > input {
            background-color: white !important;
            color: black !important;
            border: 1px solid #d0d0d0 !important;
            padding: 18px 16px !important;
            height: 70px !important;
            box-sizing: border-box !important;
            line-height: 1.4 !important;
        }

        .stTextInput > div > div > input::placeholder {
            color: transparent !important;
        }

        .stTextInput label {
            font-size: 1.15em !important;
            color: #1b4332 !important;
            margin-bottom: 8px !important;
        }

        .stSuccess {
            display: none;
        }

        .stWarning {
            display: none;
        }

        .stError {
            background: rgba(244, 67, 54, 0.1);
            border-left: 4px solid #c41c3b;
        }

        .stInfo {
            background: rgba(45, 106, 79, 0.05);
            border-left: 4px solid #40916c;
        }

        a {
            color: #2d6a4f !important;
            text-decoration: none;
            font-weight: 500;
        }

        a:hover {
            color: #1b4332 !important;
            text-decoration: underline;
        }

        .conclusion-box {
            background: linear-gradient(135deg, rgba(27, 67, 50, 0.08) 0%, rgba(45, 106, 79, 0.06) 100%);
            border-left: 5px solid #1b4332;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            font-weight: 500;
        }

        h3 {
            font-size: 1.25em;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        h4 {
            font-size: 1.1em;
            margin-top: 15px;
            margin-bottom: 8px;
        }

        .hero-gradient {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 700px;
            height: 700px;
            background: radial-gradient(circle, rgba(45, 106, 79, 0.08) 0%, rgba(45, 106, 79, 0.04) 50%, transparent 75%);
            border-radius: 50%;
            filter: blur(100px);
            z-index: 0;
            pointer-events: none;
        }

        .input-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            gap: 40px;
            position: relative;
            z-index: 1;
        }

        .input-section h1 {
            font-size: 3.5em;
            font-weight: 700;
            color: #1b4332;
            margin: 0;
            text-align: center;
            letter-spacing: -1px;
        }

        .input-section p {
            font-size: 1.35em;
            color: #558b63;
            text-align: center;
            margin: 0;
            max-width: 1000px;
            font-weight: 500;
            white-space: normal;
            word-wrap: break-word;
        }

        .input-container {
            display: flex;
            gap: 12px;
            width: 100%;
            max-width: 600px;
        }

        [data-testid="stTextInput"] {
            flex: 1;
        }

        [data-testid="stButton"] button {
            height: 70px !important;
            line-height: 1.4 !important;
            padding: 18px 24px !important;
            box-sizing: border-box !important;
        }

        .disclaimer {
            font-size: 0.95em;
            color: #a8a8a8;
            text-align: center;
            margin-top: 30px;
            line-height: 1.5;
        }
    </style>
    """, unsafe_allow_html=True)

    # 배경 데코 요소
    st.html("""
    <div class="deco-blob-1"></div>
    <div class="deco-blob-2"></div>
    <div class="hero-gradient"></div>
    """)


def initialize_session_state() -> None:
    """
    Streamlit 세션 상태를 초기화합니다.
    여러 페이지에서 공유되는 상태를 설정합니다.
    """
    if "fetch_triggered" not in st.session_state:
        st.session_state.fetch_triggered = False

    if "company_name" not in st.session_state:
        st.session_state.company_name = ""

    if "company_data" not in st.session_state:
        st.session_state.company_data = None


def get_color_for_risk_grade(grade: str) -> str:
    """
    위험 등급에 따른 색상 코드를 반환합니다.

    Args:
        grade: "high" | "medium" | "low"

    Returns:
        색상 코드 (hex)
    """
    color_map = {
        "high": "#c41c3b",
        "medium": "#f57c00",
        "low": "#2e7d32"
    }
    return color_map.get(grade.lower(), "#666666")


def get_label_for_risk_grade(grade: str) -> str:
    """
    위험 등급 코드에 해당하는 한글 라벨을 반환합니다.

    Args:
        grade: "HIGH_RISK" | "MEDIUM_RISK" | "LOW_RISK"

    Returns:
        한글 라벨
    """
    label_map = {
        "HIGH_RISK": "고위험",
        "MEDIUM_RISK": "중위험",
        "LOW_RISK": "저위험"
    }
    return label_map.get(grade, "미분류")


def show_section_header(text: str) -> None:
    """
    섹션 헤더를 표시합니다.

    Args:
        text: 헤더 텍스트
    """
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def show_analysis_card(content: str) -> None:
    """
    분석 결과를 카드 형식으로 표시합니다.

    Args:
        content: 카드에 표시할 콘텐츠 (마크다운)
    """
    st.markdown(f'<div class="analysis-card">{content}</div>', unsafe_allow_html=True)


def show_conclusion_box(title: str, content: str) -> None:
    """
    결론을 박스 형식으로 표시합니다.

    Args:
        title: 박스 제목
        content: 박스 콘텐츠
    """
    st.markdown(
        f'<div class="conclusion-box"><strong>{title}</strong><br/>{content}</div>',
        unsafe_allow_html=True
    )
