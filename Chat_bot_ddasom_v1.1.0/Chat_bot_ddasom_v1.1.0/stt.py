import os
from config import TEMP_DIR

def transcribe_audio(client, audio_data, conv_num):
    """음성을 텍스트로 변환"""
    # 임시 디렉토리 생성
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # 사용자 오디오 저장
    user_audio_path = os.path.join(TEMP_DIR, f"user_audio_{conv_num}.wav")
    with open(user_audio_path, "wb") as f:
        f.write(audio_data.read())
    
    # 음성 인식
    with open(user_audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    
    # 변환 결과 저장
    transcription_file_path = os.path.join(TEMP_DIR, f"transcription_{conv_num}.txt")
    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    
    return transcript