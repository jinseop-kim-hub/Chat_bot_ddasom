import os
from elevenlabs import ElevenLabs
from config import ELEVENLABS_API_KEY, TEMP_DIR

def init_Elevenlabs():
    """ElevenLabs 클라이언트 초기화"""
    if not ELEVENLABS_API_KEY:
        raise ValueError("환경 변수에 ELEVENLABS_API_KEY가 설정되어 있지 않습니다.")
    return ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech(client_tts, text, voice_id, conv_num):
    """텍스트를 음성으로 변환"""
    if not voice_id:
        raise ValueError("유효한 음성 ID가 필요합니다.")
    
    os.makedirs(TEMP_DIR, exist_ok=True)
    tts_output_file = os.path.join(TEMP_DIR, f"chatbot_response_audio_{conv_num}.mp3")
    
    audio_stream = client_tts.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2"
    )
    
    audio_chunks = [chunk for chunk in audio_stream]
    audio_bytes = b"".join(audio_chunks)
    
    with open(tts_output_file, "wb") as audio_file:
        audio_file.write(audio_bytes)
    
    return audio_bytes