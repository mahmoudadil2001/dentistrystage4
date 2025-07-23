import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyf9rMq1dh71Ib3nWNO7yyhrNCLmHDaYcjElk6E2k_nAEQ3x2KXo-w7q8jZIZgVOZoI/exec"

def send_telegram_message(message):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"خطأ في إرسال رسالة التليجرام: {e}")

def check_login(username, password):
    data = {"action": "check", "username": username, "password": password}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
        return res.text.strip() == "TRUE"
    except Exception as e:
        st.error(f"خطأ في التحقق من تسجيل الدخول: {e}")
        return False

def get_user_data(username):
    data = {"action": "get_user_data", "username": username}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
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
    except Exception as e:
        st.error(f"خطأ في جلب بيانات المستخدم: {e}")
        return None

def login_page():
    st.title("تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if not username or not password:
            st.warning("يرجى ملء جميع الحقول")
        else:
            if check_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = username

                user_data = get_user_data(username)
                if user_data:
                    message = (
                        f"🔑 تم تسجيل دخول المستخدم:\n"
                        f"اسم المستخدم: <b>{user_data['username']}</b>\n"
                        f"الاسم الكامل: <b>{user_data['full_name']}</b>\n"
                        f"الجروب: <b>{user_data['group']}</b>\n"
                        f"رقم الهاتف: <b>{user_data['phone']}</b>"
                    )
                    send_telegram_message(message)

                st.success(f"مرحباً {user_data['full_name']}!")
                st.experimental_rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

def forgot_password_page():
    st.title("استعادة كلمة المرور")

    username = st.text_input("اسم المستخدم", key="forgot_username")
    full_name = st.text_input("الاسم الكامل", key="forgot_full_name")

    if 'password_updated' not in st.session_state:
        st.session_state['password_updated'] = False

    if st.button("عودة"):
        st.session_state['password_updated'] = False
        st.session_state['allow_reset'] = False
        st.session_state['show_forgot'] = False
        st.experimental_rerun()

    if st.button("تحقق"):
        if not username.strip() or not full_name.strip():
            st.warning("يرجى ملء اسم المستخدم والاسم الكامل")
            st.session_state['allow_reset'] = False
        else:
            user_data = get_user_data(username)
            if user_data and user_data['full_name'].strip().lower() == full_name.strip().lower():
                st.success("✅ تم التحقق بنجاح، أدخل كلمة مرور جديدة")
                st.session_state['allow_reset'] = True
            else:
                st.error("اسم المستخدم أو الاسم الكامل غير صحيح")
                st.session_state['allow_reset'] = False

    if st.session_state.get('allow_reset', False) and not st.session_state['password_updated']:
        new_password = st.text_input("كلمة المرور الجديدة", type="password", key="new_pass")
        confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="confirm_pass")

        if st.button("تحديث كلمة المرور"):
            if new_password != confirm_password:
                st.warning("كلمة المرور غير متطابقة")
            else:
                data = {
                    "action": "update_password",
                    "username": username,
                    "full_name": full_name,
                    "new_password": new_password
                }
                try:
                    res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
                    if res.text.strip() == "UPDATED":
                        st.success("✅ تم تحديث كلمة المرور، سجل دخولك الآن")
                        st.session_state['password_updated'] = True
                        st.session_state['allow_reset'] = False
                        st.experimental_rerun()
                    else:
                        st.error("فشل في تحديث كلمة المرور")
                except Exception as e:
                    st.error(f"خطأ في تحديث كلمة المرور: {e}")
