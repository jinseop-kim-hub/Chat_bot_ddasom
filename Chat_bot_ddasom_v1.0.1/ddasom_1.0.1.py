####################################################
# 1. 필요 라이브러리 및 환경설정
####################################################
import os
import base64
import random
import uuid
import streamlit as st

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from elevenlabs import ElevenLabs

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from supabase import create_client, Client

# 환경 변수 로드 및 정리 함수
load_dotenv(find_dotenv())
def clean_env(var_name: str) -> str:
    return os.environ.get(var_name, "").strip().strip('"').strip("'")

# Supabase 환경 변수 (필요에 따라 수정)
SUPABASE_URL = clean_env("SUPABASE_URL") 
SUPABASE_KEY = clean_env("SUPABASE_KEY") 

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("환경 변수에 SUPABASE_URL 또는 SUPABASE_KEY가 설정되어 있지 않습니다.")
    st.stop()

# Supabase 클라이언트 생성 및 연결 확인
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
try:
    supabase.table("users").select("*").limit(1).execute()
except Exception as e:
    st.error(f"❌ Supabase 연결 실패: {e}")

####################################################
# 2. 데이터베이스 사용자 관리 및 음성 선택 (사이드바)
####################################################
# 사용자 관리
st.sidebar.header("🚩사용자 추가")
user_name = st.sidebar.text_input("이름")
email = st.sidebar.text_input("이메일")

if st.sidebar.button("사용자 등록"):
    user_id = str(uuid.uuid4())
    data = {"user_id": user_id, "user_name": user_name, "email": email}
    supabase.table("users").insert(data).execute()
    st.sidebar.success("✅ 사용자 추가 완료!")

user_data = supabase.table("users").select("user_id", "user_name").execute().data
if user_data:
    selected_user = st.sidebar.selectbox(
        "👨‍👩‍👧‍👦 사용자를 선택하세요",
        options=[user["user_id"] for user in user_data],
        format_func=lambda x: next(user["user_name"] for user in user_data if user["user_id"] == x)
    )
else:
    st.sidebar.warning("⚠️ 등록된 사용자가 없습니다. 사용자를 추가하세요.")

# 음성 선택 (별도 컨테이너)
with st.sidebar.container():
    # st.header("음성 선택")
    voice_names = [
        "Aria", "Roger", "Sarah", "Laura", "Charlie", "George",
        "Callum", "River", "Liam", "Charlotte", "Alice", "Matilda",
        "Will", "Jessica", "Eric", "Chris", "Brian", "Daniel", "Lily",
        "Bill", "Anna Kim", "Jennie"
    ]
    voice_options = {
        name: os.environ.get("VOICE_" + name.replace(" ", "_").upper())
        for name in voice_names
    }
    # 필터링: 등록되지 않은 음성 제거
    voice_options = {name: vid for name, vid in voice_options.items() if vid}
    if not voice_options:
        st.error("등록된 음성 옵션이 없습니다. .env 파일을 확인해주세요.")
        selected_voice_id = None
    else:
        selected_voice = st.selectbox("🔊 음성을 선택하세요", list(voice_options.keys()), key="voice_select") # label_visibility="hidden"
        selected_voice_id = voice_options[selected_voice]

####################################################
# 2.1 API 초기화 (OpenAI, ElevenLabs)
####################################################
api_key = clean_env("OPENAI_API_KEY")
if not api_key:
    st.error("환경 변수에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

elevenlabs_api_key = clean_env("ELEVENLABS_API_KEY")
if not elevenlabs_api_key:
    st.error("환경 변수에 ELEVENLABS_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

client = OpenAI(api_key=api_key)
client_tts = ElevenLabs(api_key=elevenlabs_api_key)

####################################################
# 3. 스트림릿 UI 구성 및 대화 초기화
####################################################
st.title("마음 건강 지킴이 챗봇 따솜이 🌞")
st.subheader("👵👴 어르신들의 마음 건강을 위한 챗봇입니다. 편안하게 이야기해주세요.")

st.session_state.setdefault("messages", [
    {"role": "assistant", "content": "안녕하세요 어르신! 오늘 하루는 어떠셨어요? 😊"}
])
if "conv_count" not in st.session_state:
    st.session_state["conv_count"] = 1

# 대화 메시지 출력
grandchildren = ["👦", "👧"]
grandparent = ["👴", "👵"]
for msg in st.session_state["messages"]:
    avatar_icon = random.choice(grandchildren) if msg["role"] == "assistant" else random.choice(grandparent)
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.write(msg["content"])

####################################################
# 4. 사용자 입력 및 챗봇 응답 생성
####################################################
audio_data = st.audio_input("Record a voice message")
prompt = st.chat_input("Say something")

if prompt:
    user_input = prompt.strip()
elif audio_data:
    conv_num = st.session_state["conv_count"]
    save_dir = "temp"
    os.makedirs(save_dir, exist_ok=True)
    user_audio_path = os.path.join(save_dir, f"user_audio_{conv_num}.wav")
    with open(user_audio_path, "wb") as f:
        f.write(audio_data.read())
    with open(user_audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    transcription_file_path = os.path.join(save_dir, f"transcription_{conv_num}.txt")
    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    user_input = transcript
else:
    user_input = ""

if user_input:
    conv_num = st.session_state["conv_count"]
    system_prompt = """ 
    역할: 당신은 치매 예방 전문가이자, 정서적인 지지를 제공하는 친근하고 다정한 손자 역할을 하는 챗봇 ' 따솜이 '입니다.
    당신은 노년층 사용자와 편안하고 즐거운 대화를 나누면서, 인지 능력을 활성화하고 긍정적인 감정을 유지하도록 돕는 것을 목표로 합니다.

    지시사항:
    1. 출력량: 답변은 **3문장**을 넘지 않도록 하세요.
    2. 대화 주제:주요 대화 주제는 치매 예방과 관련된 내용입니다. 
                하지만 대화가 자연스럽게 흘러갈 수 있도록 일상적인 이야기, 추억 회상, 관심사 등 
                다양한 주제를 활용하여 편안한 분위기를 조성해야 합니다.
    3. 손자 말투 & 어조: 손자, 손녀가 할머니, 할아버지께 친근하고 편안하게 이야기하는 것처럼 부드럽고, 공손하며, 긍정적인 어조를 사용하세요. 
                        "~요", "~하세요" 와 같은 존댓말을 기본으로 사용하되, 딱딱하지 않고 애교 섞인 표현을 섞어 친밀감을 높일 수 있습니다.
    4. 지속적인 대화 & 질문: 대화가 끊기지 않도록 지속적으로 질문하고, 사용자의 답변에 맞춰 자연스럽게 다음 주제로 넘어갈 수 있도록 유도하세요.
    5. 감정 분석 및 반영: 사용자의 감정을 주의 깊게 파악하고, 대화에 반영하여 공감하고 지지하는 따뜻한 반응을 보여주세요.
    
    추가 지침:
    1. 사용자의 답변을 주의 깊게 듣고, 반복적인 질문이나 엉뚱한 답변을 하지 않도록 주의하세요.
    2. 최신 정보를 활용하여 치매 예방에 대한 정확하고 유용한 정보를 제공할 수 있도록 노력하세요.
    3. 사용자가 불편하거나 불쾌감을 느낄 수 있는 주제나 표현은 피하도록 주의하세요.
    4. 개인 정보나 민감한 정보를 묻거나 요구하지 마세요.
    5. 지속적으로 대화의 품질을 개선하기 위해 노력하고, 사용자 피드백을 적극적으로 반영하세요.
    6. 답변은 **3문장**을 넘지 않도록 하세요.
    """  
    # .env에서 모델 이름 가져오기
    chat_model_name = clean_env("CHAT_MODEL") or "gpt-4o-mini"
    chat_model = ChatOpenAI(model=chat_model_name, temperature=1.0, api_key=api_key)
    conversation = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]
    response = chat_model.invoke(conversation)
    chatbot_response = response.content if hasattr(response, "content") else str(response)
    
    # 응답 저장 및 대화에 추가
    save_dir = "temp"
    os.makedirs(save_dir, exist_ok=True)
    chatbot_response_path = os.path.join(save_dir, f"chatbot_response_{conv_num}.txt")
    tts_output_file = os.path.join(save_dir, f"chatbot_response_audio_{conv_num}.mp3")
    with open(chatbot_response_path, "w", encoding="utf-8") as f:
        f.write(chatbot_response)
    
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": chatbot_response})
    
    # 데이터베이스 저장: 기존 대화 확인 및 업데이트/삽입
    chat_log_response = supabase.table("chat_log").select("id").eq("user_id", selected_user).execute()
    if chat_log_response.data:
        chat_log_id = chat_log_response.data[0]["id"]
    else:
        chat_log_id = str(uuid.uuid4())
        chat_log_data = {
            "id": chat_log_id,
            "user_id": selected_user,
            "created_chat": "now()",
            "title": f"{user_name} 대화방"
        }
        supabase.table("chat_log").insert(chat_log_data).execute()
        
    existing_message = supabase.table("message").select("id", "user_message", "response")\
                        .eq("conversation_id", chat_log_id)\
                        .eq("user_id", selected_user).execute().data
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
            "user_id": selected_user,
            "user_message": user_input,
            "response": chatbot_response,
            "sent_at": "now()"
        }
        supabase.table("message").insert(message_data).execute()
    
    # 대화 새 메시지 재출력
    for msg in st.session_state["messages"][-2:]:
        avatar_icon = random.choice(grandchildren) if msg["role"] == "assistant" else random.choice(grandparent)
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.write(msg["content"])

    ####################################################
    # 5. ElevenLabs TTS를 사용한 음성 변환 및 재생
    ####################################################
    if selected_voice_id is None:
        st.error("유효한 음성 옵션이 없어 TTS를 수행할 수 없습니다.")
        st.stop()
    
    if not os.path.exists(chatbot_response_path):
        st.error("챗봇 응답 파일이 존재하지 않습니다.")
        st.stop()
    
    with open(chatbot_response_path, "r", encoding="utf-8") as f:
        chatbot_text = f.read().strip()
    
    audio_stream = client_tts.text_to_speech.convert(
        text=chatbot_text,
        voice_id=selected_voice_id,
        model_id="eleven_multilingual_v2"
    )
    audio_chunks = [chunk for chunk in audio_stream]
    audio_bytes = b"".join(audio_chunks)
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        브라우저가 오디오 태그를 지원하지 않습니다.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    
    with open(tts_output_file, "wb") as audio_file:
        audio_file.write(audio_bytes)
    
    st.session_state["conv_count"] += 1

####################################################
# 추가: 마이크 권한 요청 (JavaScript)
####################################################
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