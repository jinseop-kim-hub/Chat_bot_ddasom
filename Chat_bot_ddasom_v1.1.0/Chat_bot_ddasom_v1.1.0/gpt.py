import streamlit as st

from openai import OpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationSummaryBufferMemory
from config import OPENAI_API_KEY, CHAT_MODEL, SYSTEM_PROMPT

def init_openai():
    """OpenAI 클라이언트 초기화"""
    if not OPENAI_API_KEY:
        raise ValueError("환경 변수에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    return OpenAI(api_key=OPENAI_API_KEY)

def memory_update(user_id,chat_model): 
    from db_utils import get_chat_memory
    if "session_memory" not in st.session_state:
        st.session_state.session_memory = ConversationSummaryBufferMemory(
            llm=chat_model, # 모델 설정시 모델이 요약해줌 단, api 부과
            memory_key="session_chat_history", 
            max_token_limit=500,  # 최대 1000 토큰까지만 저장
            return_messages=False
        )
    session_memory = st.session_state.session_memory
    conversation_pairs = get_chat_memory(user_id)
    for user_input, bot_response in conversation_pairs:
        session_memory.save_context({"input": user_input}, {"output": bot_response})

    memory_data = st.session_state.session_memory.load_memory_variables({}) 
    summary = memory_data.get("session_chat_history", "없음")
    
    return summary 

def get_chat_response(user_input,user_id):
    """GPT 모델을 사용해 챗봇 응답 생성"""
    if not OPENAI_API_KEY:
        raise ValueError("환경 변수에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    
    chat_model = ChatOpenAI(model=CHAT_MODEL, temperature=1.0, api_key=OPENAI_API_KEY)
    summary = memory_update(user_id,chat_model)
    conversation = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(content=summary),
        HumanMessage(content=user_input)
    ]
    response = chat_model.invoke(conversation)
    return response.content if hasattr(response, "content") else str(response)

def save_response(chatbot_response, conv_num):
    """응답을 파일로 저장"""
    import os
    from config import TEMP_DIR
    
    os.makedirs(TEMP_DIR, exist_ok=True)
    chatbot_response_path = os.path.join(TEMP_DIR, f"chatbot_response_{conv_num}.txt")
    
    with open(chatbot_response_path, "w", encoding="utf-8") as f:
        f.write(chatbot_response)
    
    return chatbot_response_path