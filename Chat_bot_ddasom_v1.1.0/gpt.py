from openai import OpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from config import OPENAI_API_KEY, CHAT_MODEL, SYSTEM_PROMPT

def init_openai():
    """OpenAI 클라이언트 초기화"""
    if not OPENAI_API_KEY:
        raise ValueError("환경 변수에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    return OpenAI(api_key=OPENAI_API_KEY)

def get_chat_response(user_input):
    """GPT 모델을 사용해 챗봇 응답 생성"""
    if not OPENAI_API_KEY:
        raise ValueError("환경 변수에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    
    chat_model = ChatOpenAI(model=CHAT_MODEL, temperature=1.0, api_key=OPENAI_API_KEY)
    conversation = [
        SystemMessage(content=SYSTEM_PROMPT),
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