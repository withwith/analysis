import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(
    page_title="텍스트 분석기",
    page_icon="??",
    layout="centered"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        padding: 20px;
    }
    .stRadio > label {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .required::after {
        content: " *";
        color: red;
    }
    .result-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .section-header {
        color: #1a73e8;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def clean_html_text(html_text):
    """HTML 텍스트 전처리 함수"""
    soup = BeautifulSoup(html_text, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text

def get_webpage_content(url):
    """웹페이지 내용 가져오기"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return clean_html_text(response.text)
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

def analyze_text(api_key, text):
    """텍스트 분석 함수"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = """
        다음 내용을 분석하여 아래 형식으로 정리해주세요. 각 섹션과 항목에는 적절한 이모지를 추가해주세요:

        ?? 내용 요약 (핵심 포인트 5개):
        ? 각 포인트는 번호를 매기고, 명확하게 구분되도록 작성
        ? 각 포인트 앞에 관련 이모지 추가

        ?? 주요 키워드:
        ? 각 키워드와 설명을 별도 줄에 작성
        ? 키워드는 굵게 강조
        ? 각 키워드 앞에 관련 이모지 추가

        분석할 내용:
        """
        
        response = model.generate_content(f"{prompt}\n\n{text}")
        return response.text
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"

# 사이드바에 API 설정
with st.sidebar:
    st.markdown("### ?? API 설정")
    api_selection = "Gemini"
    st.text_input("API 선택", value=api_selection, disabled=True)
    api_key = st.text_input("API 키 입력", type="password", help="API 키를 입력하세요")

# 메인 컨테이너
with st.container():
    st.title("?? 텍스트 분석기")
    
    # 입력 방식 선택
    st.markdown("### 방식 선택")
    input_type = st.radio(
        label="분석 방식을 선택하세요",
        options=["URL", "Text"],
        label_visibility="collapsed"
    )
    
    # 입력 영역
    st.markdown("### 입력")
    if input_type == "URL":
        input_content = st.text_area(
            label="URL을 입력하세요",
            placeholder="분석할 웹페이지의 URL을 입력하세요",
            label_visibility="collapsed"
        )
    else:
        input_content = st.text_area(
            label="텍스트를 입력하세요",
            placeholder="분석할 텍스트를 입력하세요",
            label_visibility="collapsed"
        )

    # 분석 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("분석 시작", type="primary", use_container_width=True)

    # 결과 표시
    if analyze_button:
        if not api_key:
            st.error("? API 키를 입력해주세요.")
        elif not input_content:
            st.error("? 분석할 내용을 입력해주세요.")
        else:
            with st.spinner("?? 분석 중..."):
                if input_type == "URL":
                    content = get_webpage_content(input_content)
                    if content.startswith("Error"):
                        st.error(f"? {content}")
                    else:
                        result = analyze_text(api_key, content)
                else:
                    result = analyze_text(api_key, input_content)

                # 결과 표시
                st.markdown("---")
                st.markdown("## ?? 분석 결과")
                st.markdown(f"""
                <div class="result-container">
                    <div style="white-space: pre-wrap;">
                    {result}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 분석 시간 표시
                st.caption(f"분석 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 푸터
st.markdown("---")
st.caption("Made with ?? using Streamlit and Gemini API")