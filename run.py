import streamlit as st
import requests
from orders import main as orders_main

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbycx6K2dBkAytd7QQQkrGkVnGkQUc0Aqs2No55dUDVeUmx8ERwaLqClhF9zhofyzPmY/exec"

# ✅ Telegram
BOT_TOKEN = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
CHAT_ID = "6283768537"

# ✅ Utility functions
def load_css(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Telegram error: {e}")

# ===========================
# Session state as cookie replacement
def set_user_session(key, value):
    st.session_state[key] = value

def get_user_session(key):
    return st.session_state.get(key, None)

def clear_user_session():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
# ===========================

# ✅ Google Sheet API functions
def check_login(username, password):
    data = {"action": "check", "username": username, "password": password}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data)
        return res.text.strip() == "TRUE"
    except:
        return False

def get_user_data(username):
    data = {"action": "get_user_data", "username": username}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data)
        text = res.text.strip()
        if text == "NOT_FOUND":
            return None
        parts = text.split(",")
        if len(parts) == 5:
            return {
                "username": parts[0],
                "password": parts[1],
                "full_name": parts[2],
                "group": parts[3],
                "phone": parts[4]
            }
        return None
    except:
        return None

# ✅ Login

def login_page():
    st.title("🔐 تسجيل الدخول")

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False

    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False

    if not st.session_state['show_signup']:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")

        if st.button("دخول"):
            if check_login(username, password):
                user_data = get_user_data(username)
                if user_data:
                    set_user_session("username", user_data["full_name"])
                    message = (
                        f"🔑 تم تسجيل دخول المستخدم:\n"
                        f"اسم المستخدم: <b>{user_data['username']}</b>\n"
                        f"كلمة المرور: <b>{user_data['password']}</b>\n"
                        f"الاسم الكامل: <b>{user_data['full_name']}</b>\n"
                        f"الجروب: <b>{user_data['group']}</b>\n"
                        f"رقم الهاتف: <b>{user_data['phone']}</b>"
                    )
                    send_telegram_message(message)
                    st._rerun()
                else:
                    st.error("فشل في جلب بيانات المستخدم")
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("إنشاء حساب جديد"):
                st.session_state['show_signup'] = True
                st._rerun()
        with col2:
            if st.button("هل نسيت كلمة المرور؟"):
                st.session_state['show_forgot'] = True
                st._rerun()

    else:
        signup_page()

def signup_page():
    st.title("📝 إنشاء حساب جديد")
    st.info("💡 هذه الوظيفة تحتاج إلى دمج مع Google Sheets لإضافة مستخدم.")
    if st.button("🔙 العودة لتسجيل الدخول"):
        st.session_state['show_signup'] = False
        st._rerun()

# ✅ Main app

def main():
    load_css("styles.css")

    username_cookie = get_user_session("username")

    if username_cookie:
        st.sidebar.success(f"مرحبًا، {username_cookie}")
        if st.sidebar.button("🚪 تسجيل خروج"):
            clear_user_session()
            st._rerun()
        else:
            orders_main()
    else:
        if st.session_state.get("show_forgot"):
            st.title("📤 نسيت كلمة المرور؟")
            st.info("هذه الصفحة تحتاج تطويرًا للتعامل مع الاستعادة.")
            if st.button("🔙 العودة"):
                st.session_state['show_forgot'] = False
                st._rerun()
        else:
            login_page()

if __name__ == "__main__":
    main()
