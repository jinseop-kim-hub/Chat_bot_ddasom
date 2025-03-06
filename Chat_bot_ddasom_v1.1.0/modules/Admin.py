import streamlit as st
from db_utils import init_supabase
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv, find_dotenv

def show_admin():
    load_dotenv(find_dotenv())
    
    # 환경 변수에서 비밀번호 로드
    admin_password = os.environ.get("ADMIN_PASSWORD", "").strip().strip('"').strip("'")
    
    if not admin_password:
        st.error("환경 변수에 ADMIN_PASSWORD가 설정되지 않았습니다.")
        st.stop()
    
    # 관리자 비밀번호 입력 요소 배치
    col1, col2 = st.columns([1, 80])
    with col2:
        admin_pwd_input = st.text_input("Admin PW", type="password")
    
    if admin_pwd_input != admin_password:
        st.warning("관리자 비밀번호를 입력하세요.")
        st.stop()

    st.title("관리자 대시보드")
    st.subheader("DB 텍스트 데이터를 이용한 워드클라우드")
    
    supabase = init_supabase()
    try:
        chat_logs = supabase.table("chat_log").select("title").execute().data
        if chat_logs:
            text_data = " ".join([log["title"] for log in chat_logs if log.get("title")])
            wc = WordCloud(width=800, height=400, background_color="white").generate(text_data)
            plt.figure(figsize=(10, 5))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)
        else:
            st.info("표시할 데이터가 없습니다.")
    except Exception as e:
        st.error(f"대시보드 오류: {e}")