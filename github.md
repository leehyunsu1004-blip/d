# 대한민국 천만 관객 영화 흥행 기록 분석 앱

위키백과 [대한민국의 영화 흥행 기록](https://ko.wikipedia.org/wiki/대한민국의_영화_흥행_기록) 문서에서 천만 관객을 돌파한 한국 영화 데이터를 웹 스크래핑으로 수집하고, 데이터를 정제하여 시각화하는 Streamlit 웹 애플리케이션입니다.

## 주요 기능

1. **웹 데이터 수집**: `requests`와 `BeautifulSoup`을 사용하여 지정된 위키백과 페이지의 HTML을 가져오고, 조건(`관객수`, `감독` 열 포함)에 맞는 첫 번째 표를 파싱합니다.
2. **데이터 전처리 및 정제**:
   - 각주 태그(`sup`) 및 영화 제목의 꺾쇠괄호(`《》`) 제거
   - 관객수 텍스트를 정수형(int) 숫자로 변환
   - 개봉일에서 `개봉연도`와 `개봉월` 파생 변수 추출
3. **데이터 시각화 대시보드**:
   - 핵심 요약 지표 (천만 영화 총 편수, 역대 1위 영화, 1위 관객수)
   - 정제된 전체 데이터 표 출력
   - 관객수 상위 10편 가로 막대 차트
   - 개봉연도별 천만 영화 편수 막대 차트

## 기술 스택

- **Language**: Python 3.8+
- **Web Framework**: Streamlit
- **Data Processing**: Pandas
- **Web Scraping**: Requests, BeautifulSoup4

## 설치 및 실행 방법

1. 저장소 클론 및 폴더 이동
```bash
git clone https://github.com/사용자아이디/저장소이름.git
cd 저장소이름
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. Streamlit 앱 실행 (파이썬 파일명이 `app.py`인 경우)
```bash
streamlit run app.py
```