import hmac  # 建議放在檔案最上方的 import 區塊

# ==================== Admin 密碼驗證 ====================
def check_admin_password() -> bool:
    try:
        expected_password = st.secrets.get("admin_password", "")
    except StreamlitSecretNotFoundError:
        expected_password = ""

    if not expected_password:
        st.error("尚未設定管理員密碼，請在 secrets.toml 或 Streamlit Secrets 中設定 admin_password。")
        st.stop()

    if st.session_state.get("admin_authenticated", False):
        return True

    st.subheader("🔒 管理員登入")
    with st.form("admin_login_form"):
        password_input = st.text_input("請輸入管理員密碼（Admin Password）", type="password")
        submitted = st.form_submit_button("登入系統")

    if submitted:
        if hmac.compare_digest(password_input, str(expected_password)):
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("密碼錯誤，請重新輸入。")

    return False


if not check_admin_password():
    st.stop()