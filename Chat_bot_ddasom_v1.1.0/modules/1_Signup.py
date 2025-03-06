import streamlit as st
from db_utils import init_supabase, add_user

def main():
    st.title("회원가입")
    st.subheader("새로운 회원가입을 진행해주세요.")

    user_name = st.text_input("이름", key="signup_name")
    email = st.text_input("이메일", key="signup_email")
    
    if st.button("회원가입"):
        if user_name and email:
            supabase = init_supabase()
            # 기존에 동일 이메일이 등록되어 있으면 회원가입 불가
            result = supabase.table("users").select("*").eq("email", email).execute()
            if result.data:
                st.error("해당 이메일은 이미 등록되어 있습니다. 로그인 페이지에서 로그인해주세요.")
            else:
                user_id = add_user(supabase, user_name, email)
                st.success(f"회원가입 완료! 사용자 ID: {user_id}")
                st.session_state["authenticated_user"] = user_id
        else:
            st.warning("이름과 이메일을 모두 입력해주세요.")

if __name__ == "__main__":
    main()