import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# ������ �⺻ ����
st.set_page_config(
    page_title="�ؽ�Ʈ �м���",
    page_icon="??",
    layout="centered"
)

# CSS ��Ÿ��
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
    """HTML �ؽ�Ʈ ��ó�� �Լ�"""
    soup = BeautifulSoup(html_text, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text

def get_webpage_content(url):
    """�������� ���� ��������"""
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
    """�ؽ�Ʈ �м� �Լ�"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = """
        ���� ������ �м��Ͽ� �Ʒ� �������� �������ּ���. �� ���ǰ� �׸񿡴� ������ �̸����� �߰����ּ���:

        ?? ���� ��� (�ٽ� ����Ʈ 5��):
        ? �� ����Ʈ�� ��ȣ�� �ű��, ��Ȯ�ϰ� ���еǵ��� �ۼ�
        ? �� ����Ʈ �տ� ���� �̸��� �߰�

        ?? �ֿ� Ű����:
        ? �� Ű����� ������ ���� �ٿ� �ۼ�
        ? Ű����� ���� ����
        ? �� Ű���� �տ� ���� �̸��� �߰�

        �м��� ����:
        """
        
        response = model.generate_content(f"{prompt}\n\n{text}")
        return response.text
    except Exception as e:
        return f"�м� �� ������ �߻��߽��ϴ�: {str(e)}"

# ���̵�ٿ� API ����
with st.sidebar:
    st.markdown("### ?? API ����")
    api_selection = "Gemini"
    st.text_input("API ����", value=api_selection, disabled=True)
    api_key = st.text_input("API Ű �Է�", type="password", help="API Ű�� �Է��ϼ���")

# ���� �����̳�
with st.container():
    st.title("?? �ؽ�Ʈ �м���")
    
    # �Է� ��� ����
    st.markdown("### ��� ����")
    input_type = st.radio(
        label="�м� ����� �����ϼ���",
        options=["URL", "Text"],
        label_visibility="collapsed"
    )
    
    # �Է� ����
    st.markdown("### �Է�")
    if input_type == "URL":
        input_content = st.text_area(
            label="URL�� �Է��ϼ���",
            placeholder="�м��� ���������� URL�� �Է��ϼ���",
            label_visibility="collapsed"
        )
    else:
        input_content = st.text_area(
            label="�ؽ�Ʈ�� �Է��ϼ���",
            placeholder="�м��� �ؽ�Ʈ�� �Է��ϼ���",
            label_visibility="collapsed"
        )

    # �м� ��ư
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("�м� ����", type="primary", use_container_width=True)

    # ��� ǥ��
    if analyze_button:
        if not api_key:
            st.error("? API Ű�� �Է����ּ���.")
        elif not input_content:
            st.error("? �м��� ������ �Է����ּ���.")
        else:
            with st.spinner("?? �м� ��..."):
                if input_type == "URL":
                    content = get_webpage_content(input_content)
                    if content.startswith("Error"):
                        st.error(f"? {content}")
                    else:
                        result = analyze_text(api_key, content)
                else:
                    result = analyze_text(api_key, input_content)

                # ��� ǥ��
                st.markdown("---")
                st.markdown("## ?? �м� ���")
                st.markdown(f"""
                <div class="result-container">
                    <div style="white-space: pre-wrap;">
                    {result}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # �м� �ð� ǥ��
                st.caption(f"�м� �Ϸ� �ð�: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Ǫ��
st.markdown("---")
st.caption("Made with ?? using Streamlit and Gemini API")