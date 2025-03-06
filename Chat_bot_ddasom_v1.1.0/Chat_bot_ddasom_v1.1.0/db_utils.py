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

def get_chat_memory(user_id):
    """사용자의 최신 10개 대화만 가져옵니다다."""
    supabase = init_supabase()
    
    # 🔹 가장 최신의 user_message와 response 가져오기 (1개의 레코드만 가져옴)
    response = supabase.table("message").select("user_message, response")\
                .eq("user_id", user_id)\
                .order("sent_at", desc=True)\
                .execute()
    
    if not response.data:
        return []

    # 🔹 데이터에서 메시지 추출 (여러 줄로 저장된 데이터를 \n 기준으로 분리)
    latest_entry = response.data[0]
    user_message_raw = latest_entry["user_message"]
    bot_response_raw = latest_entry["response"]

    # 🔹 \n 기준으로 데이터 분할 (정확한 분리가 안 될 경우 대비)
    user_messages = user_message_raw.strip().split("\n") if user_message_raw else []
    bot_responses = bot_response_raw.strip().split("\n") if bot_response_raw else []

    # 🔹 최신 10개의 메시지만 유지
    user_messages = user_messages[-10:]  # 마지막 10개
    bot_responses = bot_responses[-10:]  # 마지막 10개


    # 🔹 (사용자 메시지, 챗봇 응답) 형식으로 반환
    messages = list(zip(user_messages, bot_responses))

    return messages

def get_full_chat_history(user_id):
    """사용자의 전체 대화 기록을 가져오는 함수."""
    supabase = init_supabase()
    
    # 🔹 user_message와 response 전체 가져오기 (최신순 정렬)
    response = supabase.table("message").select("user_message, response").eq("user_id", user_id).order("sent_at", desc=True).execute()
    messages = response.data if response.data else []

    # 🔹 전체 대화 내용을 (사용자 메시지, 챗봇 응답) 형태로 변환
    full_conversation = []
    for msg in messages:
        user_messages = msg["user_message"].strip().split("\n") if msg["user_message"] else []
        bot_responses = msg["response"].strip().split("\n") if msg["response"] else []

        # 🔹 각 메시지를 순서대로 추가
        for user_msg, bot_msg in zip(user_messages, bot_responses):
            full_conversation.append((user_msg, bot_msg))

    return full_conversation

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