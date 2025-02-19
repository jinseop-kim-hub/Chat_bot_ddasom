import os
import base64
import streamlit as st
import random
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from elevenlabs import ElevenLabs

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# .env 파일에서 환경 변수 로드
load_dotenv(find_dotenv())

# OpenAI API 키 가져오기 (없으면 오류 처리)
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("환경 변수에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

# ELEVENLABS_API_KEY 가져오기 (없으면 오류 처리)
elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
if not elevenlabs_api_key:
    st.error("환경 변수에 ELEVENLABS_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# ElevenLabs TTS 클라이언트 초기화
client_tts = ElevenLabs(api_key=elevenlabs_api_key)

#####
# 스트림릿 UI 구성
#####
st.title("마음 건강 지킴이 챗봇 따솜이 🌞")
st.subheader("👵👴 어르신들의 마음 건강을 위한 챗봇입니다. 편안하게 이야기해주세요.")

# 세션 스테이트에 대화 내역이 없으면 한 번만 초기 메시지 설정
st.session_state.setdefault("messages", [
    {"role": "assistant", "content": "안녕하세요 어르신! 오늘 하루는 어떠셨어요? 😊"}
])

# 대화 번호(세션) 초기화
if "conv_count" not in st.session_state:
    st.session_state["conv_count"] = 1

grandchildren = ["👦", "👧"]
grandparent =  ["👴", "👵"]
# 기존 대화 메시지 한 번만 출력
for msg in st.session_state["messages"]:
    avatar_icon = random.choice(grandchildren) if msg["role"] == "assistant" else random.choice(grandparent)  # 원하는 이모지로 변경

    with st.chat_message(msg["role"], avatar = avatar_icon):
        st.write(msg["content"])

# 파일 경로: /c:/Users/hn000/Desktop/senior chatbot/web-ui/gpt_TTS_1.py

##########################
# 분기점: 텍스트 입력 vs. 음성 입력
##########################
audio_data = st.audio_input("Record a voice message")
prompt = st.chat_input("Say something")

if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
    user_input = prompt.strip()
elif audio_data:
    conv_num = st.session_state["conv_count"]
    # st.audio(audio_data, format="audio/wav") #내가 말한거 듣는거
    save_dir = "temp"
    os.makedirs(save_dir, exist_ok=True)
    user_audio_path = os.path.join(save_dir, f"user_audio_{conv_num}.wav")
    with open(user_audio_path, "wb") as f:
        f.write(audio_data.read())
    
    transcription_file_path = os.path.join(save_dir, f"transcription_{conv_num}.txt")
    with open(user_audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    user_input = transcript
else:
    user_input = ""

# 질문이 있을 경우 챗봇 응답 생성 및 TTS 변환 진행
if user_input:
    conv_num = st.session_state["conv_count"]
    system_prompt = """ 
    역할: 당신은 치매 예방 전문가이자, 정서적인 지지를 제공하는 친근하고 다정한 손주 역할을 하는 챗봇 ' 따솜이 '입니다. 당신은 노년층 사용자와 편안하고 즐거운 대화를 나누면서, 인지 능력을 활성화하고 긍정적인 감정을 유지하도록 돕는 것을 목표로 합니다.

    지시사항:
    출력량: 답변은 **3문장** 넘지 않도록 하세요.
    대화 주제: 주요 대화 주제는 치매 예방과 관련된 내용입니다. 하지만 대화가 자연스럽게 흘러갈 수 있도록 일상적인 이야기, 추억 회상, 관심사 등 다양한 주제를 활용하여 편안한 분위기를 조성해야 합니다.
    손자 말투 & 어조: 손자, 손녀가 할머니, 할아버지께 친근하고 편안하게 이야기하는 것처럼 부드럽고, 공손하며, 긍정적인 어조를 사용하세요. "~요", "~하세요" 와 같은 존댓말을 기본으로 사용하되, 딱딱하지 않고 애교 섞인 표현을 섞어 친밀감을 높일 수 있습니다.
    지속적인 대화 & 질문: 대화가 끊기지 않도록 지속적으로 질문하고, 사용자의 답변에 맞춰 자연스럽게 다음 주제로 넘어갈 수 있도록 유도하세요.
    감정 분석 및 반영: 사용자의 감정을 주의 깊게 파악하고, 대화에 반영하여 공감하고 지지하는 따뜻한 반응을 보여주세요.
    추가 지침:
    사용자의 답변을 주의 깊게 듣고, 반복적인 질문이나 엉뚱한 답변을 하지 않도록 주의하세요.
    최신 정보를 활용하여 치매 예방에 대한 정확하고 유용한 정보를 제공할 수 있도록 노력하세요.
    사용자가 불편하거나 불쾌감을 느낄 수 있는 주제나 표현은 피하도록 주의하세요.
    개인 정보나 민감한 정보를 묻거나 요구하지 마세요.
    지속적으로 대화의 품질을 개선하기 위해 노력하고, 사용자 피드백을 적극적으로 반영하세요.
    답변은 **3문장** 넘지 않도록 하세요.
    """  
    
    chat_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=1.0,
        api_key=api_key
    )
    conversation = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]
    response = chat_model.invoke(conversation)
    chatbot_response = response.content if hasattr(response, "content") else str(response)
    
    save_dir = "temp"
    chatbot_response_path = os.path.join(save_dir, f"chatbot_response_{conv_num}.txt")
    tts_output_file = os.path.join(save_dir, f"chatbot_response_audio_{conv_num}.mp3")
    
    with open(chatbot_response_path, "w", encoding="utf-8") as f:
        f.write(chatbot_response)
    
    # 기존 대화에 새 사용자 질문과 챗봇 응답 추가
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": chatbot_response})
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 메세지 재 출력부분
    # 새 메시지 출력 (전체 대화를 다시 표시)
    for msg in st.session_state["messages"][-2:]:
        st.chat_message(msg["role"],avatar = avatar_icon).write(msg["content"])
    
    # st.success(f"챗봇 응답이 저장되었습니다: {chatbot_response_path}")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ##########################
    # 4. ElevenLabs TTS API를 사용한 챗봇 응답 음성 변환
    ##########################
    if not os.path.exists(chatbot_response_path):
        st.error("챗봇 응답 파일이 존재하지 않습니다.")
        st.stop()
    
    with open(chatbot_response_path, "r", encoding="utf-8") as f:
        chatbot_text = f.read().strip()
    
    audio_stream = client_tts.text_to_speech.convert(
        text=chatbot_text,
        voice_id="uyVNoMrnUku1dZyVEXwD",  # 사용하려는 voice_id로 변경하세요.
        model_id="eleven_multilingual_v2"  # 필요에 따라 모델 ID 수정
    )
    
    audio_chunks = []
    for chunk in audio_stream:
        audio_chunks.append(chunk)
    audio_bytes = b"".join(audio_chunks)
    
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        브라우저가 오디오 태그를 지원하지 않습니다.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True) # 대답한거 듣는거 
    
    with open(tts_output_file, "wb") as audio_file:
        audio_file.write(audio_bytes)
    
    # st.success(f"TTS 음성 파일이 저장되었습니다: {tts_output_file}") # 재출력 부분
    
    # 대화 번호 증가 (다음 대화를 위해)
    st.session_state["conv_count"] += 1
    