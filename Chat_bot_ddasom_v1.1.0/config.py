import os
from dotenv import load_dotenv, find_dotenv

# 환경 변수 로드
load_dotenv(find_dotenv())

# 환경 변수 정리 함수
def clean_env(var_name: str) -> str:
    """환경 변수를 정리해 반환합니다."""
    return os.environ.get(var_name, "").strip().strip('"').strip("'")

# API 키 및 환경설정
OPENAI_API_KEY = clean_env("OPENAI_API_KEY")
ELEVENLABS_API_KEY = clean_env("ELEVENLABS_API_KEY")
SUPABASE_URL = clean_env("SUPABASE_URL")
SUPABASE_KEY = clean_env("SUPABASE_KEY")
CHAT_MODEL = clean_env("CHAT_MODEL") or "gpt-4o-mini"

# 음성 목록 설정
VOICE_NAMES = [
    "Aria", "Roger", "Sarah", "Laura", "Charlie", "George",
    "Callum", "River", "Liam", "Charlotte", "Alice", "Matilda",
    "Will", "Jessica", "Eric", "Chris", "Brian", "Daniel", "Lily",
    "Bill", "Anna Kim", "Jennie"
]

# 음성 ID 매핑
def get_voice_options():
    """음성 이름과 ID를 매핑해 반환합니다."""
    voice_options = {
        name: clean_env("VOICE_" + name.replace(" ", "_").upper())
        for name in VOICE_NAMES
    }
    # 필터링: 등록되지 않은 음성 제거
    return {name: vid for name, vid in voice_options.items() if vid}

# 시스템 프롬프트
SYSTEM_PROMPT = """ 
역할: 당신은 치매 예방 전문가이자, 정서적인 지지를 제공하는 친근하고 다정한 손자 역할을 하는 챗봇 ' 따솜이 '입니다.
당신은 노년층 사용자와 편안하고 즐거운 대화를 나누면서, 인지 능력을 활성화하고 긍정적인 감정을 유지하도록 돕는 것을 목표로 합니다.
당신은 하단의 '지시사항' 과 '추가 지침'을 반드시 따라야합니다.

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

# 임시 파일 저장 디렉토리
TEMP_DIR = "temp"