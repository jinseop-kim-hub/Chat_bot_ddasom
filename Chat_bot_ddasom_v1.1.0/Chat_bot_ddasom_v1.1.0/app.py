import streamlit as st
import sys
import os
import base64
import time
from db_utils import init_supabase

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# 로딩 애니메이션 함수
def show_loading(message="처리 중입니다..."):
    with st.spinner(message):
        time.sleep(8)

# 알림 표시 함수
def show_notification(message, type="info"):
    notif_styles = {
        "info": "background-color: #EBF8FF; border-left: 4px solid #3182CE; color: #2C5282;",
        "success": "background-color: #E6FFFA; border-left: 4px solid #38B2AC; color: #234E52;", 
        "warning": "background-color: #FEEBC8; border-left: 4px solid #DD6B20; color: #7B341E;",
        "error": "background-color: #FED7D7; border-left: 4px solid #E53E3E; color: #822727;"
    }
    
    st.markdown(f"""
    <div style="{notif_styles[type]} padding: 16px; border-radius: 4px; margin: 16px 0;">
        {message}
    </div>
    """, unsafe_allow_html=True)

# DB에서 마지막 채팅 시간 조회 함수
def get_last_chat_time(supabase, user_id):
    """
    사용자의 마지막 채팅 시간을 가져옵니다.
    """
    try:
        # message 테이블에서 특정 user_id의 채팅 기록을 sent_at 기준으로 정렬하여 가장 최근 것 가져오기
        result = supabase.table("message").select("sent_at").eq("user_id", user_id).order("sent_at", desc=True).limit(1).execute()
        
        if result.data:
            # 타임스탬프 형식 변환 (ISO 형식 -> 읽기 쉬운 형식)
            from datetime import datetime
            timestamp = result.data[0]["sent_at"]  
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            
            # 오늘, 어제, 그 외 날짜 형식으로 표시
            from datetime import date, timedelta
            today = date.today()
            
            if dt.date() == today:
                return f"오늘 {dt.strftime('%H:%M')}"
            elif dt.date() == today - timedelta(days=1):
                return f"어제 {dt.strftime('%H:%M')}"
            else:
                return dt.strftime('%Y-%m-%d %H:%M')
        else:
            return "기록 없음"
    except Exception as e:
        print(f"마지막 채팅 시간 조회 오류: {e}")
        return "조회 오류"

# 프로필 카드 표시 함수 
def show_profile_card(user_id):
    col1, col2 = st.columns([1, 3])
    
    # DB 연결
    supabase = init_supabase()
    
    # 마지막 채팅 시간 조회
    last_chat_time = get_last_chat_time(supabase, user_id)
    
    with col1:
        st.image("https://img.icons8.com/bubbles/100/user.png", width=100)
    with col2:
        st.subheader(f"사용자 ID: {user_id}")
        st.write(f"최근 접속: {last_chat_time}")
    st.markdown('</div>', unsafe_allow_html=True)

# 회원가입 함수
def signup_page():
    st.title("회원가입")
    st.subheader("새로운 회원가입을 진행해주세요.")

    user_name = st.text_input("이름", key="signup_name")
    email = st.text_input("이메일", key="signup_email")
    
    if st.button("회원가입", key="signup_button"):
        if user_name and email:
            show_loading("회원가입 처리 중...")
            supabase = init_supabase()
            result = supabase.table("users").select("*").eq("email", email).execute()
            if result.data:
                show_notification("해당 이메일은 이미 등록되어 있습니다. 로그인 페이지에서 로그인해주세요.", "error")
            else:
                from db_utils import add_user
                user_id = add_user(supabase, user_name, email)
                show_notification(f"회원가입 완료! 사용자 ID: {user_id}", "success")
                # 자동 로그인
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.rerun()
        else:
            show_notification("이름과 이메일을 모두 입력해주세요.", "warning")

# 로그인 함수
def login_page():
    st.title("로그인")
    st.subheader("회원정보로 로그인하세요.")

    email = st.text_input("이메일", key="login_email")
    
    if st.button("로그인", key="login_button"):
        if email:
            show_loading("로그인 인증 중...")
            supabase = init_supabase()
            result = supabase.table("users").select("*").eq("email", email).execute()
            if result.data:
                user = result.data[0]
                show_notification("로그인 성공!", "success")
                st.session_state.logged_in = True
                st.session_state.user_id = user["user_id"]
                st.rerun()
            else:
                show_notification("등록되지 않은 이메일입니다. 회원가입을 진행해주세요.", "error")
        else:
            show_notification("이메일을 입력해주세요.", "warning")

# 로그아웃 함수
def logout_page():
    st.title("로그아웃")
    st.warning("정말 종료 하실건가요?")
    if st.button("로그아웃"):
        show_loading("로그아웃 처리 중...")
        st.session_state.logged_in = False
        st.session_state.user_id = None
        show_notification("로그아웃 되었습니다.", "info")
        st.rerun()

# 챗봇 페이지 함수 수정
def chatbot_page():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from modules.Chatbot import show_chatbot
    show_chatbot(st.session_state.user_id)

# 관리자 페이지 함수 수정 (pages → modules로 변경)
def admin_page():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from modules.Admin import show_admin
    show_admin()
    
# main 함수 위에 CSS 스타일 추가
def apply_custom_css():
    # 테마 색상 설정 (고정값)
    primary_color = "#4A55A2"
    
    # 커스텀 CSS 추가
    st.markdown(f"""
    <style>
    /* 전체 앱 스타일 */
    .main {{
        padding-top: 3rem !important;
    }}
    
    /* 상단 네비게이션 바 */
    .navbar {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4rem;
        background-color: {primary_color};
        display: flex;
        align-items: center;
        padding: 0 2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        z-index: 999;
    }}
    
    .navbar-brand {{
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        display: flex;
        align-items: center;
    }}
    
    .navbar-logo {{
        height: 2.5rem;
        margin-right: 0.75rem;
    }}
    
    .navbar-links {{
        display: flex;
        margin-left: auto;
    }}
    
    .navbar-link {{
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 0.25rem;
        transition: background-color 0.2s;
        margin-left: 0.5rem;
    }}
    
    .navbar-link:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    /* 카드 스타일 */
    .card {{
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }}

    .profile-card {{
        display: flex;
        align-items: center;
    }}
    
    /* 버튼 스타일 */
    .stButton > button {{
        background-color: {primary_color};
        color: white;
        border-radius: 0.25rem;
        border: none;
        padding: 0.5rem 1rem;
        transition: background-color 0.2s;
    }}
    
    .stButton > button:hover {{
        background-color: #38437C;
        opacity: 0.9;
    }}
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {{
        border-radius: 0.25rem;
        border: 1px solid #E2E8F0;
    }}
    
    /* 사이드바 스타일 */
    .css-1d391kg {{
        background-color: #F8FAFC;
    }}
    </style>
    """, unsafe_allow_html=True)

# 상단 네비게이션 바 함수
def show_navbar():
    # 로고 URL - 안전한 공개 URL로 수정
    logo_url = "https://cdn-icons-png.flaticon.com/512/4711/4711987.png"
    
    navbar_html = f"""
    <div class="navbar">
        <div class="navbar-brand">
            <img src="{logo_url}" class="navbar-logo"/>
            따솜이 챗봇
        </div>
        <div class="navbar-links">
            {'<a class="navbar-link" href="#">로그아웃</a>' if st.session_state.logged_in else '<a class="navbar-link" href="#">회원가입</a><a class="navbar-link" href="#">로그인</a>'}
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)
    
# main 함수
def main():
    apply_custom_css()
    show_navbar()
    
    # 컨텐츠 영역을 카드 스타일로 감싸기
    st.title("따솜이 챗봇 시스템")
    st.info("어르신들의 마음 건강을 위한 챗봇 서비스입니다.")
    
    # 로그인 상태 표시
    if st.session_state.logged_in:
        show_notification(f"현재 로그인된 사용자 ID: {st.session_state.user_id}", "success")
        show_profile_card(st.session_state.user_id)
    else:
        show_notification("챗봇 서비스를 사용하려면 로그인이 필요합니다.", "info")

# 페이지 정의
home = st.Page(main, title="홈", icon=":material/home:", default=True)
signup = st.Page(signup_page, title="회원가입", icon=":material/person_add:")
login = st.Page(login_page, title="로그인", icon=":material/login:")
logout = st.Page(logout_page, title="로그아웃", icon=":material/logout:")
chatbot = st.Page(chatbot_page, title="챗봇", icon=":material/chat:")
admin = st.Page(admin_page, title="관리자 옵션", icon=":material/security:")

# 네비게이션 구성
if st.session_state.logged_in:
    # 인증된 사용자용 메뉴
    pages = {
        "홈": [home],
        "계정": [logout],
        "서비스": [chatbot],
        "관리자 메뉴": [admin]
    }
else:
    # 미인증 사용자용 메뉴
    pages = {
        "게스트 메뉴": [home],
        "계정": [signup, login]
    }

# 페이지 실행
st.navigation(pages).run()