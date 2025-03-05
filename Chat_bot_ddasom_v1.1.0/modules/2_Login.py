import streamlit as st
from db_utils import init_supabase

def main():
    st.title("로그인")
    st.subheader("회원정보로 로그인하세요.")

    email = st.text_input("이메일", key="login_email")
    
    if st.button("로그인"):
        if email:
            supabase = init_supabase()
            # 이메일로 사용자 조회
            result = supabase.table("users").select("*").eq("email", email).execute()
            if result.data:
                user = result.data[0]
                st.success(f"로그인 성공! 사용자 ID: {user['user_id']}")
                st.session_state["authenticated_user"] = user["user_id"]
            else:
                st.error("등록된 이메일이 없습니다. 먼저 회원가입을 진행해주세요.")
        else:
            st.warning("이메일을 입력해주세요.")
            
if __name__ == "__main__":
    main()