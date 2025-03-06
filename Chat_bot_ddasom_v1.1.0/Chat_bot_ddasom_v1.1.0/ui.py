import random
import streamlit as st
import os
import base64
from config import get_voice_options, TEMP_DIR

def setup_page(user_id):
    """페이지 기본 설정 및 세션 상태 초기화"""
    st.title("마음 건강 지킴이 챗봇 따솜이 🌞")
    st.subheader("👵👴 어르신들의 마음 건강을 위한 챗봇입니다. 편안하게 이야기해주세요.")

    """전체 대화 기록 가져오기"""
    if "selected_user" not in st.session_state or st.session_state.selected_user != user_id:
            st.session_state.selected_user = user_id  
        
            from db_utils import get_full_chat_history
            """전체 대화 기록 가져오기"""
            chat_history = get_full_chat_history(user_id)
        
            if chat_history:
                # 🔹 데이터베이스에서 불러온 내용을 채팅 형식으로 변환
                st.session_state.messages = [
                    {"role": "user", "content": user_msg} if idx % 2 == 0 
                    else {"role": "assistant", "content": bot_msg} 
                    for idx, (user_msg, bot_msg) in enumerate(chat_history)
                ]
            else:
                # ✅ 데이터가 없으면 기본 메시지 출력
                st.session_state.messages = [
                    {"role": "assistant", "content": "안녕하세요 어르신! 오늘 하루는 어떠셨어요? 😊"}
                ]
    
    st.session_state["conv_count"] = 1

def setup_sidebar():
    """사이드바 설정"""
    st.sidebar.header("🔊 음성 선택")
    
    # 음성 선택 컨테이너
    with st.sidebar.container():
        voice_options = get_voice_options()
        if not voice_options:
            st.error("등록된 음성 옵션이 없습니다. .env 파일을 확인해주세요.")
            selected_voice_id = None
        else:
            selected_voice = st.selectbox(" ", list(voice_options.keys()), key="voice_select")
            selected_voice_id = voice_options[selected_voice]
    
    return selected_voice_id


def display_messages():
    """대화 메시지 표시"""
    grandchildren = ["👦", "👧"]
    grandparent = ["👴", "👵"]
    for msg in st.session_state["messages"]:
        avatar_icon = random.choice(grandchildren) if msg["role"] == "assistant" else random.choice(grandparent)
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.write(msg["content"])

def get_user_input():
    """사용자 입력 받기"""
    audio_data = st.audio_input("Record a voice message")
    prompt = st.chat_input("Say something")
    
    if prompt:
        return prompt.strip(), None
    elif audio_data:
        return None, audio_data
    else:
        return None, None

def update_chat(user_input, chatbot_response):
    """채팅 내역 업데이트"""
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": chatbot_response})
    
    # 새 메시지만 표시
    display_new_messages()
    
    st.session_state["conv_count"] += 1

def display_new_messages():
    """새로 추가된 메시지만 표시"""
    grandchildren = ["👦", "👧"]
    grandparent = ["👴", "👵"]
    for msg in st.session_state["messages"][-2:]:
        avatar_icon = random.choice(grandchildren) if msg["role"] == "assistant" else random.choice(grandparent)
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.write(msg["content"])

def play_audio(audio_bytes):
    """오디오 재생"""
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        브라우저가 오디오 태그를 지원하지 않습니다.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def request_mic_permission():
    """마이크 권한 요청"""
    html_code = """
    <script>
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => console.log("마이크 권한 허용됨"))
      .catch(err => {
          console.error("마이크 권한 거부:", err);
          alert("마이크 권한이 거부되었습니다. 브라우저 설정에서 허용해주세요.");
      });
    </script>
    """
    st.components.v1.html(html_code, height=0)

def ensure_temp_dir():
    """임시 디렉토리 확인 및 생성"""
    os.makedirs(TEMP_DIR, exist_ok=True)