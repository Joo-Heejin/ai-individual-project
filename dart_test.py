# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
import OpenDartReader
import pandas as pd
from datetime import datetime
import re

sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("🔄 DART API 데이터 수집 테스트 (정기공시 전문화)")
print("💡 최초 실행 시 데이터 다운로드로 인해 30초~1분 정도 소요될 수 있습니다.")
print("   잠시만 기다려주세요...")
print("="*60 + "\n")

# 환경변수 로드
load_dotenv(".env")
api_key = os.getenv("DART_API_KEY")

if not api_key:
    raise ValueError("❌ DART_API_KEY가 .env 파일에 설정되어 있지 않습니다.")

# OpenDartReader 초기화
try:
    dart = OpenDartReader(api_key)
    print("✅ OpenDartReader 초기화 완료\n")
except Exception as e:
    print(f"❌ OpenDartReader 초기화 실패: {e}")
    exit(1)


def search_company(dart, company_name):
    """기업명으로 검색하여 기업 코드 반환"""
    try:
        print(f"🔍 기업 검색 중: '{company_name}'...")

        # 기업 검색
        results = dart.company_by_name(company_name)

        if not results:
            raise ValueError(f"'{company_name}'을(를) 찾을 수 없습니다.")

        # 상장사 우선 선택, 없으면 첫 번째 선택
        corp_info = None
        for result in results:
            if result.get('corp_cls') == 'Y':  # 상장사만 필터링
                corp_info = result
                break

        if not corp_info:
            corp_info = results[0]

        corp_code = corp_info['corp_code']
        corp_name = corp_info['corp_name']

        print(f"✅ 기업 발견: {corp_name} (코드: {corp_code})\n")
        return corp_code, corp_name

    except Exception as e:
        print(f"❌ 기업 검색 실패: {e}")
        return None, None


def get_periodic_report(dart, corp_code, corp_name):
    """정기 공시(사업보고서 > 반기보고서 > 분기보고서 우선순위) 조회"""
    try:
        print(f"📋 {corp_name}의 정기 공시 검색 중...")

        # 전체 공시 목록
        all_filings = dart.list(corp=corp_code)

        if all_filings.empty:
            raise ValueError("공시를 찾을 수 없습니다.")

        # 우선순위: 사업보고서 > 반기보고서 > 분기보고서
        business_reports = all_filings[
            all_filings['report_nm'].str.contains('사업보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        semi_reports = all_filings[
            all_filings['report_nm'].str.contains('반기보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        quarter_reports = all_filings[
            all_filings['report_nm'].str.contains('분기보고서', na=False) &
            ~all_filings['report_nm'].str.contains('\[수정', na=False)
        ]

        # 우선순위대로 선택
        selected_filing = None
        selected_type = None

        if not business_reports.empty:
            selected_filing = business_reports.iloc[0]
            selected_type = '사업보고서'
        elif not semi_reports.empty:
            selected_filing = semi_reports.iloc[0]
            selected_type = '반기보고서'
        elif not quarter_reports.empty:
            selected_filing = quarter_reports.iloc[0]
            selected_type = '분기보고서'

        if selected_filing is None:
            raise ValueError("정기 공시를 찾을 수 없습니다.")

        report_nm = selected_filing['report_nm']
        rcept_no = selected_filing['rcept_no']
        rcept_dt = selected_filing['rcept_dt']

        print(f"✅ {selected_type} 발견: {report_nm} (접수: {rcept_dt})\n")
        return selected_filing, selected_type

    except Exception as e:
        import traceback
        print(f"❌ 정기 공시 검색 실패: {e}")
        traceback.print_exc()
        return None, None


def extract_financial_statement(dart, corp_code):
    """재무제표 추출"""
    try:
        print("📊 재무제표 추출 중...\n")

        from datetime import datetime
        current_year = datetime.now().year

        # 현재 연도와 작년부터 시작해서 데이터를 찾기
        fs_data = None
        for year in [current_year, current_year - 1, current_year - 2]:
            try:
                fs_data = dart.finstate_all(corp_code, str(year))
                if fs_data is not None and not fs_data.empty:
                    break
            except:
                continue

        if fs_data is None or fs_data.empty:
            print("⚠️  재무제표 데이터가 없습니다.")
            return None

        # DataFrame 형태 (이미 DataFrame)
        df = fs_data

        print("📌 재무제표 데이터 (상위 10줄):")
        print("-" * 80)
        print(df.head(10).to_string())
        print("-" * 80)
        print(f"총 {len(df)}개 항목\n")

        return df

    except Exception as e:
        print(f"⚠️  재무제표 추출 실패: {e}\n")
        return None


def extract_notes_from_document(dart, rcept_no):
    """공시 문서에서 주석 섹션의 텍스트 추출"""
    try:
        print("📝 재무제표 주석 추출 중...\n")

        # 1단계: XML 문서 조회
        doc_xml = dart.document(rcept_no)

        if not doc_xml:
            print("⚠️  문서 조회 실패")
            return None

        # 2단계: 목차 조회로 주석 섹션 확인
        toc_df = dart.sub_docs(rcept_no)

        if toc_df.empty:
            print("⚠️  목차 조회 실패")
            return None

        # 3단계: 주석 관련 항목 찾기
        notes_items = toc_df[
            (toc_df['title'].str.contains('주석', na=False)) |
            (toc_df['title'].str.contains('재무제표', na=False) &
             toc_df['title'].str.contains('주석', na=False))
        ]

        if not notes_items.empty:
            print(f"✅ 주석 항목 발견:")
            for idx, row in notes_items.head(3).iterrows():
                print(f"   - {row['title']}")
            notes_title = notes_items.iloc[0]['title']
        else:
            # 주석이 없으면 경영진검토와 전망 또는 다른 정성정보 찾기
            other_items = toc_df[
                (toc_df['title'].str.contains('경영진', na=False)) |
                (toc_df['title'].str.contains('사업결과', na=False))
            ]
            if not other_items.empty:
                notes_title = other_items.iloc[0]['title']
            else:
                notes_title = None

        # 4단계: XML에서 텍스트 추출
        if notes_title:
            # XML에서 주석 섹션 추출 (간단한 정규식 사용)
            # 실제 구현에서는 더 정교한 파싱 필요
            notes_text = extract_text_from_xml(doc_xml, rcept_no)
        else:
            notes_text = None

        # 5단계: 결과 출력
        if notes_text:
            print("📌 재무제표 주석 텍스트 (처음 500자):")
            print("-" * 80)
            print(notes_text[:500] + "...")
            print("-" * 80)
            print(f"총 {len(notes_text)}자\n")
        else:
            # 대체 정보 제공
            toc_info = f"보고서 목차:\n"
            for idx, row in toc_df.head(15).iterrows():
                toc_info += f"- {row['title']}\n"
            print("📌 보고서 목차 정보:")
            print("-" * 80)
            print(toc_info)
            print("-" * 80)
            notes_text = toc_info

        return notes_text

    except Exception as e:
        print(f"⚠️  공시 정보 추출 실패: {e}\n")
        return None


def extract_text_from_xml(xml_content, rcept_no):
    """XML 문서에서 텍스트 추출 (정성정보)"""
    try:
        # XML에서 <P> 태그 내용 추출
        p_tags = re.findall(r'<P[^>]*>([^<]+)</P>', xml_content)
        extracted_text = ' '.join(p_tags)

        # 정상적인 텍스트만 필터링
        extracted_text = re.sub(r'<[^>]+>', '', extracted_text)  # 남은 HTML 태그 제거
        extracted_text = extracted_text.strip()

        if extracted_text and len(extracted_text) > 100:
            return extracted_text
        else:
            # XML이 너무 크면 일부만 추출
            return f"공시 접수번호: {rcept_no}\n문서 형식: XBRL 기반 구조화 공시\n상세 내용은 DART 웹사이트에서 확인하실 수 있습니다."

    except:
        return None


# 메인 실행
if __name__ == "__main__":
    try:
        # 1. 기업 검색
        corp_code, corp_name = search_company(dart, "하이브")

        if not corp_code:
            print("💡 '삼성전자'로 재검색 중...\n")
            corp_code, corp_name = search_company(dart, "삼성전자")

        if not corp_code:
            raise ValueError("검색 실패")

        # 2. 정기 공시 조회 (사업보고서 우선)
        report, report_type = get_periodic_report(dart, corp_code, corp_name)

        if report is None:
            raise ValueError("정기 공시 조회 실패")

        rcept_no = report['rcept_no']

        # 3. 재무제표 추출
        financial_df = extract_financial_statement(dart, corp_code)

        # 4. 재무제표 주석 추출
        notes = extract_notes_from_document(dart, rcept_no)

        # 완료 메시지
        print("="*60)
        print("✅ 데이터 수집 완료!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}\n")
        exit(1)
