import uuid
import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def init_supabase():
    """Supabase 클라이언트를 초기화합니다."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("환경 변수에 SUPABASE_URL 또는 SUPABASE_KEY가 설정되어 있지 않습니다.")
        st.stop()
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        supabase.table("users").select("*").limit(1).execute()
        return supabase
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {e}")
        st.stop()

def add_user(supabase, user_name, email):
    """새 사용자를 데이터베이스에 추가합니다."""
    user_id = str(uuid.uuid4())
    data = {"user_id": user_id, "user_name": user_name, "email": email}
    supabase.table("users").insert(data).execute()
    return user_id

def get_users(supabase):
    """모든 사용자 목록을 가져옵니다."""
    return supabase.table("users").select("user_id", "user_name").execute().data

def save_conversation(supabase, user_id, user_input, chatbot_response, user_name=None):
    """대화를 데이터베이스에 저장합니다."""
    # 기존 대화 확인 및 업데이트/삽입
    chat_log_response = supabase.table("chat_log").select("id").eq("user_id", user_id).execute()
    if chat_log_response.data:
        chat_log_id = chat_log_response.data[0]["id"]
    else:
        chat_log_id = str(uuid.uuid4())
        chat_log_data = {
            "id": chat_log_id,
            "user_id": user_id,
            "created_chat": "now()",
            "title": f"{user_name if user_name else '사용자'} 대화방"
        }
        supabase.table("chat_log").insert(chat_log_data).execute()
        
    existing_message = supabase.table("message").select("id", "user_message", "response")\
                      .eq("conversation_id", chat_log_id)\
                      .eq("user_id", user_id).execute().data
    if existing_message:
        message_id = existing_message[0]["id"]
        updated_message = existing_message[0]["user_message"] + "\n" + user_input
        updated_response = existing_message[0]["response"] + "\n" + chatbot_response
        supabase.table("message").update({"user_message": updated_message, "response": updated_response})\
                .eq("id", message_id).execute()
    else:
        message_data = {
            "id": str(uuid.uuid4()),
            "conversation_id": chat_log_id,
            "user_id": user_id,
            "user_message": user_input,
            "response": chatbot_response,
            "sent_at": "now()"
        }
        supabase.table("message").insert(message_data).execute()