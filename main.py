
import re
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup


# 1. 웹페이지 HTML을 가져오는 함수
def fetch_html(url):
    # 수업 실습용임을 밝히는 User-Agent 설정 (위키백과 접근 차단 방지)
    headers = {
        "User-Agent": "PythonClassPracticeBot/1.0 (University 1st-year non-major data analysis class)"
    }
    try:
        # 10초 제한시간(timeout)을 두고 페이지 요청
        response = requests.get(url, headers=headers, timeout=10)
        # 404, 500 등의 HTTP 오류가 발생하면 예외를 일으킴
        response.raise_for_status()
        return response.text, None
    except requests.exceptions.Timeout:
        return None, "시간 초과 오류가 발생했습니다. 인터넷 연결 상태를 확인해 주세요."
    except requests.exceptions.ConnectionError:
        return None, "연결 실패 오류가 발생했습니다. 주소가 올바른지 확인해 주세요."
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP 오류가 발생했습니다: {e}"
    except requests.exceptions.RequestException as e:
        return None, f"요청 중 알 수 없는 오류가 발생했습니다: {e}"


# 2. HTML에서 조건에 맞는 표를 찾아 DataFrame으로 변환하는 함수
def parse_movie_table(html):
    soup = BeautifulSoup(html, "html.parser")
    # class가 'wikitable'인 모든 표 찾기
    tables = soup.find_all("table", class_="wikitable")

    target_table = None
    for table in tables:
        first_row = table.find("tr")
        if first_row:
            # 첫 줄의 제목 칸(th) 텍스트 추출
            headers = [th.get_text(strip=True) for th in first_row.find_all("th")]
            # '관객수'(또는 '관객 수')와 '감독'이 모두 포함된 첫 번째 표 선택
            has_audience = any("관객" in h for h in headers)
            has_director = any("감독" in h for h in headers)
            if has_audience and has_director:
                target_table = table
                break

    # 조건에 맞는 표를 찾지 못한 경우
    if target_table is None:
        return None, "문서에서 '관객수'와 '감독' 열이 포함된 표를 찾지 못했습니다."

    # 표 내부의 모든 각주 태그(sup) 제거
    for sup in target_table.find_all("sup"):
        sup.decompose()

    rows = target_table.find_all("tr")
    # 첫 줄(tr)에서 열 이름(th) 추출
    columns = [th.get_text(strip=True) for th in rows[0].find_all("th")]

    # 나머지 줄(tr)에서 데이터 칸(td) 추출
    data = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if cells:
            row_data = [cell.get_text(strip=True) for cell in cells]
            # 열 개수와 데이터 칸 개수가 일치하는 행만 추가
            if len(row_data) == len(columns):
                data.append(row_data)

    df = pd.DataFrame(data, columns=columns)
    return df, None


# 3. 수집한 데이터를 분석하기 좋게 정제하는 함수
def clean_movie_data(df):
    df = df.copy()

    # 열 이름의 공백 통일 (예: '관객 수' -> '관객수')
    df.columns = [col.replace(" ", "") for col in df.columns]

    # 제목 열 찾기 및 꺾쇠괄호(《, 》) 제거
    title_col = [c for c in df.columns if "제목" in c or "작품" in c][0]
    df[title_col] = df[title_col].str.replace("《", "", regex=False).str.replace("》", "", regex=False)
    df = df.rename(columns={title_col: "제목"})

    # 관객수 열 찾기 및 숫자(정수)로 변환
    aud_col = [c for c in df.columns if "관객" in c][0]
    # 숫자 이외의 문자(쉼표, '명' 등) 제거 후 정수 변환
    df["관객수"] = df[aud_col].apply(lambda x: int(re.sub(r"[^0-9]", "", str(x))) if re.search(r"[0-9]", str(x)) else 0)

    # 개봉일 열 찾기 및 개봉연도, 개봉월 추출
    date_col = [c for c in df.columns if "개봉" in c][0]
    # '2014년 7월 30일' 또는 '2014.07.30' 형태에서 연도와 월 추출
    extracted_dates = df[date_col].str.extract(r"(\d{4})\D+(\d{1,2})")
    df["개봉연도"] = pd.to_numeric(extracted_dates[0], errors="coerce").fillna(0).astype(int)
    df["개봉월"] = pd.to_numeric(extracted_dates[1], errors="coerce").fillna(0).astype(int)

    # 관객수 기준 내림차순 정렬
    df = df.sort_values(by="관객수", ascending=False).reset_index(drop=True)
    return df


# 4. 화면에 지표, 표, 차트를 출력하는 함수
def display_dashboard(df):
    st.subheader("핵심 요약 지표")
    col1, col2, col3 = st.columns(3)

    # 천만 영화 수, 역대 1위 영화명, 1위 관객수 계산
    total_count = len(df)
    top_movie = df.iloc[0]["제목"]
    top_audience = df.iloc[0]["관객수"]

    col1.metric("천만 영화 수", f"{total_count}편")
    col2.metric("역대 1위", top_movie)
    col3.metric("1위 관객수", f"{top_audience:,}명")

    st.divider()

    # 정제된 전체 데이터 표 출력
    st.subheader("천만 관객 한국 영화 목록")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # 관객수 상위 10편 가로 막대 차트
    st.subheader("관객수 상위 10편 (단위: 명)")
    top10_df = df.head(10).set_index("제목")["관객수"]
    st.bar_chart(top10_df, horizontal=True)

    # 개봉연도별 편수 막대 차트
    st.subheader("개봉연도별 천만 영화 편수")
    # 연도 정보가 정상 추출된 데이터만 필터링 후 연도순 정렬
    valid_years = df[df["개봉연도"] > 0]
    year_counts = valid_years["개봉연도"].value_counts().sort_index()
    year_counts.index = year_counts.index.astype(str) + "년"
    st.bar_chart(year_counts)


# 5. 메인 앱 실행 함수
def main():
    st.set_page_config(page_title="한국 영화 흥행 기록 분석", layout="wide")
    st.title("천만 관객 한국 영화 데이터 수집 및 분석")

    default_url = "https://ko.wikipedia.org/wiki/대한민국의_영화_흥행_기록"
    # 주소를 입력받는 텍스트 입력창
    url = st.text_input("위키백과 문서 주소를 입력하세요:", value=default_url)

    # 수집 및 분석 실행 버튼
    if st.button("데이터 수집 및 분석 실행"):
        if not url.strip():
            st.warning("주소를 입력해 주세요.")
            return

        with st.spinner("데이터를 가져오고 분석하는 중입니다..."):
            # 1단계: HTML 가져오기
            html, error = fetch_html(url)
            if error:
                st.error(error)
                return

            # 2단계: 표 파싱하기
            raw_df, error = parse_movie_table(html)
            if error:
                st.error(error)
                return

            # 3단계: 데이터 정제하기
            clean_df = clean_movie_data(raw_df)

            # 4단계: 결과 화면 출력하기
            display_dashboard(clean_df)


if __name__ == "__main__":
    main()