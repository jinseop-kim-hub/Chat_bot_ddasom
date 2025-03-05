import streamlit as st
from db_utils import init_supabase, get_users, save_conversation
from ui import (setup_page, setup_sidebar, display_messages, get_user_input, 
               update_chat, play_audio, request_mic_permission, ensure_temp_dir)
from gpt import init_openai, get_chat_response, save_response
from stt import transcribe_audio
from tts import init_Elevenlabs, text_to_speech

def show_chatbot(user_id):
    ensure_temp_dir()
    
    try:
        supabase = init_supabase()
        client_openai = init_openai()
        client_tts = init_Elevenlabs()
    except Exception as e:
        st.error(f"API 초기화 오류: {e}")
        st.stop()
    
    setup_page()
    
    # 사이드바에서 음성 선택 설정
    selected_voice_id = setup_sidebar()
    
    user_data = get_users(supabase)
    selected_user = user_id

    display_messages()
    
    text_input, audio_input = get_user_input()
    user_input = ""
    if text_input:
        user_input = text_input
    elif audio_input:
        try:
            conv_num = st.session_state.get("conv_count", 1)
            user_input = transcribe_audio(client_openai, audio_input, conv_num)
        except Exception as e:
            st.error(f"음성 인식 오류: {e}")
    
    if user_input:
        try:
            conv_num = st.session_state.get("conv_count", 1)
            chatbot_response = get_chat_response(user_input)
            save_response(chatbot_response, conv_num)
            
            save_conversation(supabase, selected_user, user_input, chatbot_response)
            
            update_chat(user_input, chatbot_response)
            
            # 선택된 음성 ID로 음성 합성
            if selected_voice_id:
                audio_bytes = text_to_speech(client_tts, chatbot_response, selected_voice_id, conv_num)
                play_audio(audio_bytes)
        except Exception as e:
            st.error(f"대화 처리 오류: {e}")
    
    request_mic_permission()