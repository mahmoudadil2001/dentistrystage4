import streamlit as st
import requests
import re
import uuid
from streamlit_javascript import st_javascript

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyC1_kj-yAWT_wzQx3BGerNxAyDxZiRO7eoQmk11ywBwiPEv8nWy2_VuoIzcvTR3w2T/exec"  # غيره لرابط سكربتك

def send_telegram_message(message):
    bot_token = "ضع_توكن_البوت"
    chat_id = "ضع_معرف_الشات"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def check_login(username, password):
    res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "check", "username": username, "password": password})
    return res.text.strip() == "TRUE"

def get_user_data(username):
    res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_user_data", "username": username})
    parts = res.text.strip().split(",")
    if len(parts) == 5:
        return {
            "username": parts[0],
            "password": parts[1],
            "full_name": parts[2],
            "group": parts[3],
            "phone": parts[4]
        }
    return None

def add_user(username, password, full_name, group, phone):
    res_all = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_all_users"}).text.strip()
    if res_all:
        lines = res_all.split("\n")
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                existing_username = parts[0].strip().lower()
                existing_fullname = parts[1].strip().lower()
                if existing_username == username.lower():
                    return "USERNAME_EXISTS"
                if existing_fullname == full_name.lower():
                    return "FULLNAME_EXISTS"

    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "add",
        "username": username,
        "password": password,
        "full_name": full_name,
        "group": group,
        "phone": phone
    })
    return res.text.strip()

def set_session_token(username, token):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "set_session_token",
        "username": username,
        "token": token
    })
    return res.text.strip() == "TOKEN_SAVED"

def get_user_by_token(token):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "get_user_by_token",
        "token": token
    })
    parts = res.text.strip().split(",")
    if len(parts) == 5:
        return {
            "username": parts[0],
            "password": parts[1],
            "full_name": parts[2],
            "group": parts[3],
            "phone": parts[4]
        }
    return None

def update_password(username, new_password):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "update_password",
        "username": username,
        "new_password": new_password
    })
    return res.text.strip() == "UPDATED"

def find_username_by_last4(full_name, last4):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "find_username_by_last4",
        "full_name": full_name,
        "last4": last4
    })
    return res.text.strip()

def validate_iraqi_phone(phone):
    pattern = re.compile(
        r"^(?:"  
        r"(0(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"
        r"|"
        r"(\+964(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"
        r"|"
        r"(00964(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"
        r"|"
        r"(0(1\d{2})\d{7})"
        r")$"
    )
    return bool(pattern.match(phone))

def validate_username(username):
    return bool(username and len(username) <= 10 and re.fullmatch(r"[A-Za-z0-9_.-]+", username))

def validate_full_name(full_name):
    words = full_name.strip().split()
    if len(words) != 3:
        return False
    arabic_pattern = re.compile(r"^[\u0600-\u06FF]+$")
    for w in words:
        if len(w) > 10 or not arabic_pattern.match(w):
            return False
    return True

def validate_password(password):
    return bool(password and 4 <= len(password) <= 16)

def validate_group(group):
    return bool(group and len(group) == 1 and re.fullmatch(r"[A-Za-z]", group))

def save_token_js(token: str):
    js_code = f"localStorage.setItem('session_token', '{token}');"
    st_javascript(js_code)

def remove_token_js():
    st_javascript("localStorage.removeItem('session_token');")

def get_token_js():
    token = st_javascript("localStorage.getItem('session_token');")
    return token

def login_page():
    if "mode" not in st.session_state:
        st.session_state.mode = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # محاولة تسجيل دخول تلقائي باستخدام التوكن المخزن
    if not st.session_state.logged_in:
        token = get_token_js()
        if token:
            user = get_user_by_token(token)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_data = user

    if st.session_state.logged_in:
        st.header(f"مرحباً بك يا {st.session_state.user_data['full_name']} في صفحة الأسئلة!")
        if st.button("تسجيل خروج"):
            st.session_state.clear()
            remove_token_js()
            st.experimental_rerun()
        return

    if st.session_state.mode == "login":
        st.header("🔑 تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")

        if st.button("تسجيل الدخول"):
            if check_login(username, password):
                user = get_user_data(username)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    new_token = str(uuid.uuid4())
                    set_session_token(username, new_token)  # حفظ التوكن في شيت
                    save_token_js(new_token)  # حفظ التوكن في localStorage
                    send_telegram_message(f"✅ تسجيل دخول:\n{user}")
                    st.experimental_rerun()
                else:
                    st.error("❌ خطأ في جلب بيانات المستخدم")
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

        if st.button("إنشاء حساب جديد"):
            st.session_state.mode = "signup"
            st.experimental_rerun()

        if st.button("نسيت كلمة المرور؟"):
            st.session_state.mode = "forgot"
            st.experimental_rerun()

    elif st.session_state.mode == "signup":
        st.header("📝 إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم", key="signup_username")
        p = st.text_input("كلمة المرور", type="password", key="signup_password")
        f = st.text_input("الاسم الثلاثي (بالعربي)", key="signup_full_name")
        g = st.text_input("الجروب", key="signup_group")
        ph = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("إنشاء الحساب"):
            if not (u and p and f and g and ph):
                st.warning("❗ يرجى ملء جميع الحقول")
            elif not validate_username(u):
                st.error("❌ اسم المستخدم غير صالح (حتى 10 أحرف/أرقام/رموز بدون فراغات)")
            elif not validate_password(p):
                st.error("❌ كلمة المرور يجب أن تكون بين 4 و 16 رمز")
            elif not validate_full_name(f):
                st.error("❌ الاسم الكامل يجب أن يكون 3 كلمات بالعربي وكل كلمة ≤ 10 أحرف")
            elif not validate_group(g):
                st.error("❌ الجروب يجب أن يكون حرف واحد بالإنجليزي")
            elif not validate_iraqi_phone(ph):
                st.error("❌ رقم الهاتف غير صالح")
            else:
                res = add_user(u, p, f, g, ph)
                if res == "USERNAME_EXISTS":
                    st.error("❌ اسم المستخدم موجود")
                elif res == "FULLNAME_EXISTS":
                    st.error("❌ الاسم الكامل موجود مسبقًا")
                elif res == "ADDED":
                    st.success("✅ تم إنشاء الحساب بنجاح. الرجاء تسجيل الدخول الآن.")
                    st.session_state.signup_username = ""
                    st.session_state.signup_password = ""
                    st.session_state.signup_full_name = ""
                    st.session_state.signup_group = ""
                    st.session_state.signup_phone = ""
                    st.session_state.mode = "login"
                    st.experimental_rerun()
                else:
                    st.error("❌ حدث خطأ غير متوقع")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.experimental_rerun()

    elif st.session_state.mode == "forgot":
        st.header("🔒 استعادة كلمة المرور")
        full_name = st.text_input("✍️ اكتب اسمك الثلاثي")

        if st.button("متابعة"):
            res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_all_users"}).text.strip()
            found = any(full_name.strip().lower() == line.split(",")[1].strip().lower() for line in res.split("\n"))
            if not full_name.strip():
                st.warning("❗ الرجاء إدخال الاسم الكامل")
            elif found:
                st.session_state.temp_fullname = full_name
                st.session_state.mode = "forgot_last4"
                st.experimental_rerun()
            else:
                st.error("❌ الاسم الكامل غير موجود")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.experimental_rerun()

    elif st.session_state.mode == "forgot_last4":
        st.subheader(f"✅ الاسم: {st.session_state.temp_fullname}")
        last4 = st.text_input("📱 اكتب آخر 4 أرقام من رقم هاتفك")

        if st.button("تحقق"):
            username = find_username_by_last4(st.session_state.temp_fullname, last4)
            if username != "NOT_FOUND":
                st.success(f"✅ تم التحقق. اسم المستخدم: {username}")
                st.session_state.forgot_username = username
                st.session_state.mode = "forgot_new_password"
                st.experimental_rerun()
            else:
                st.error("❌ لم يتم العثور على المستخدم")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "forgot"
            st.experimental_rerun()

    elif st.session_state.mode == "forgot_new_password":
        st.subheader(f"🔑 إعادة تعيين كلمة المرور للمستخدم: {st.session_state.forgot_username}")
        new_pass = st.text_input("كلمة المرور الجديدة", type="password")
        new_pass_confirm = st.text_input("تأكيد كلمة المرور الجديدة", type="password")

        if st.button("تغيير كلمة المرور"):
            if not new_pass or not new_pass_confirm:
                st.warning("❗ يرجى ملء الحقول")
            elif new_pass != new_pass_confirm:
                st.error("❌ كلمة المرور غير متطابقة")
            elif not validate_password(new_pass):
                st.error("❌ كلمة المرور يجب أن تكون بين 4 و 16 رمز")
            else:
                if update_password(st.session_state.forgot_username, new_pass):
                    st.success("✅ تم تغيير كلمة المرور بنجاح. الرجاء تسجيل الدخول.")
                    st.session_state.mode = "login"
                    st.experimental_rerun()
                else:
                    st.error("❌ حدث خطأ في تحديث كلمة المرور")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "forgot_last4"
            st.experimental_rerun()

if __name__ == "__main__":
    login_page()
