# -*- coding: utf-8 -*-
"""
DART API 데이터 수집 및 추출 모듈
기업 검색, 공시 조회, 재무제표 및 주석 추출 기능 제공
"""

import os
import re
from typing import Optional, Tuple, Any
import pandas as pd
from datetime import datetime
import dart_fss as dart


def init_dart_api() -> Any:
    """
    OpenDartReader 초기화

    Returns:
        OpenDartReader 인스턴스

    Raises:
        ValueError: DART_API_KEY가 설정되지 않은 경우
    """
    dart_api_key = os.getenv("DART_API_KEY")

    # Streamlit Cloud의 Secrets에서도 시도
    if not dart_api_key:
        try:
            import streamlit as st
            dart_api_key = st.secrets.get("DART_API_KEY")
        except:
            pass

    if not dart_api_key:
        raise ValueError("❌ DART_API_KEY가 .env 파일에 설정되어 있지 않습니다.")

    try:
        dart.set_api_key(dart_api_key)
        return dart
    except Exception as e:
        raise ValueError(f"❌ DART API 초기화 실패: {e}")


def search_company(dart_module: Any, company_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    기업명으로 검색하여 기업 코드 반환 (dart-fss 사용)
    상장사를 우선 선택하고 없으면 첫 번째 결과 반환

    Args:
        dart_module: dart_fss 모듈
        company_name: 검색할 기업명

    Returns:
        (corp_code, corp_name) 튜플 또는 (None, None)
    """
    try:
        # dart-fss의 search API 사용
        results = dart_module.search(company_name)

        if not results or len(results) == 0:
            return None, None

        corp_info = None

        # 1. 상장사(corp_cls == 'Y') 중 정확히 매치
        for result in results:
            if result.get('corp_cls') == 'Y' and result.get('corp_name') == company_name:
                corp_info = result
                break

        # 2. 상장사 중 첫 번째
        if not corp_info:
            for result in results:
                if result.get('corp_cls') == 'Y':
                    corp_info = result
                    break

        # 3. 정확히 매치 (비상장사 포함)
        if not corp_info:
            for result in results:
                if result.get('corp_name') == company_name:
                    corp_info = result
                    break

        # 4. 그냥 첫 번째
        if not corp_info and len(results) > 0:
            corp_info = results[0]

        if corp_info:
            return corp_info.get('corp_code'), corp_info.get('corp_name')
        return None, None

    except Exception as e:
        return None, None


def get_periodic_report(
    dart: Any,
    corp_code: str,
    corp_name: str
) -> Tuple[Optional[pd.Series], Optional[str]]:
    """
    정기 공시 조회 (사업보고서 > 반기보고서 > 분기보고서 우선순위)

    Args:
        dart: OpenDartReader 인스턴스
        corp_code: 기업 코드
        corp_name: 기업명 (로깅용)

    Returns:
        (공시 정보 Series, 공시 유형) 튜플 또는 (None, None)
    """
    try:
        all_filings = dart.list(corp=corp_code)
        if all_filings.empty:
            return None, None

        # 사업보고서 (최우선)
        business_reports = all_filings[
            all_filings['report_nm'].str.contains('사업보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        if not business_reports.empty:
            return business_reports.iloc[0], '사업보고서'

        # 반기보고서
        semi_reports = all_filings[
            all_filings['report_nm'].str.contains('반기보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        if not semi_reports.empty:
            return semi_reports.iloc[0], '반기보고서'

        # 분기보고서
        quarter_reports = all_filings[
            all_filings['report_nm'].str.contains('분기보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        if not quarter_reports.empty:
            return quarter_reports.iloc[0], '분기보고서'

        return None, None
    except:
        return None, None


def extract_financial_statement(dart: Any, corp_code: str) -> Optional[pd.DataFrame]:
    """
    재무제표 추출 (현재 연도부터 역순으로 3년치 시도)

    Args:
        dart: OpenDartReader 인스턴스
        corp_code: 기업 코드

    Returns:
        재무제표 DataFrame 또는 None
    """
    try:
        current_year = datetime.now().year
        fs_data = None

        for year in [current_year, current_year - 1, current_year - 2]:
            try:
                fs_data = dart.finstate_all(corp_code, str(year))
                if fs_data is not None and not fs_data.empty:
                    return fs_data
            except:
                continue

        return None
    except:
        return None


def extract_notes(dart: Any, rcept_no: str) -> Optional[str]:
    """
    공시 문서에서 주석 텍스트 추출 (간단 버전)

    Args:
        dart: OpenDartReader 인스턴스
        rcept_no: 공시 접수 번호

    Returns:
        주석 텍스트 또는 None
    """
    try:
        doc_xml = dart.document(rcept_no)
        if not doc_xml:
            return None

        p_tags = re.findall(r'<P[^>]*>([^<]+)</P>', doc_xml)
        text = ' '.join(p_tags)
        text = re.sub(r'<[^>]+>', '', text).strip()

        return text if len(text) > 100 else None
    except:
        return None


def extract_text_from_xml(xml_content: str, rcept_no: str) -> Optional[str]:
    """
    XML 문서에서 텍스트 추출 (정성정보)

    Args:
        xml_content: XML 문서 문자열
        rcept_no: 공시 접수 번호

    Returns:
        추출된 텍스트 또는 None
    """
    try:
        p_tags = re.findall(r'<P[^>]*>([^<]+)</P>', xml_content)
        extracted_text = ' '.join(p_tags)

        extracted_text = re.sub(r'<[^>]+>', '', extracted_text)
        extracted_text = extracted_text.strip()

        if extracted_text and len(extracted_text) > 100:
            return extracted_text
        else:
            return f"공시 접수번호: {rcept_no}\n문서 형식: XBRL 기반 구조화 공시\n상세 내용은 DART 웹사이트에서 확인하실 수 있습니다."
    except:
        return None


def extract_notes_from_document(dart: Any, rcept_no: str) -> Optional[str]:
    """
    공시 문서에서 주석 섹션의 텍스트 추출 (상세 버전)
    목차를 조회하여 주석 항목을 찾은 후 추출

    Args:
        dart: OpenDartReader 인스턴스
        rcept_no: 공시 접수 번호

    Returns:
        주석 텍스트 또는 보고서 목차 정보
    """
    try:
        doc_xml = dart.document(rcept_no)
        if not doc_xml:
            return None

        toc_df = dart.sub_docs(rcept_no)
        if toc_df.empty:
            return None

        # 주석 관련 항목 찾기
        notes_items = toc_df[
            (toc_df['title'].str.contains('주석', na=False)) |
            (toc_df['title'].str.contains('재무제표', na=False) &
             toc_df['title'].str.contains('주석', na=False))
        ]

        if not notes_items.empty:
            notes_title = notes_items.iloc[0]['title']
        else:
            other_items = toc_df[
                (toc_df['title'].str.contains('경영진', na=False)) |
                (toc_df['title'].str.contains('사업결과', na=False))
            ]
            if not other_items.empty:
                notes_title = other_items.iloc[0]['title']
            else:
                notes_title = None

        # XML에서 텍스트 추출
        if notes_title:
            notes_text = extract_text_from_xml(doc_xml, rcept_no)
        else:
            notes_text = None

        # 결과 반환
        if notes_text:
            return notes_text
        else:
            toc_info = "보고서 목차:\n"
            for idx, row in toc_df.head(15).iterrows():
                toc_info += f"- {row['title']}\n"
            return toc_info

    except:
        return None
