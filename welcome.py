import streamlit as st
from datetime import datetime
import requests

def send_to_telegram(name, group):
    telegram_token = "77e4dab0d9568f41dadd61befe71d71405ba0c4d"
    chat_id = "5993975957"
    message = f"🟢 مستخدم جديد:\n👤 الاسم: {name}\n👥 القروب: {group}\n🕒 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except:
        pass

def show_welcome():
    with st.container():
        st.markdown(
            """
            <div style="background-color:#f0f2f6; padding:30px; border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h1 style="text-align:center; color:#3E64FF;">🌟 مرحباً بك في Dentistry Stage 4 🌟</h1>
                <p style="text-align:center; font-size:18px;">🚀 منصة تجمع طلاب المرحلة الرابعة في طب الأسنان — مرحباً بك في رحلتك العلمية!</p>
                <hr>
            """,
            unsafe_allow_html=True
        )

        with st.form("welcome_form"):
            st.markdown("### ✍️ أدخل معلوماتك للبدء")
            name = st.text_input("👤 اسمك")
            group = st.text_input("👥 قروبك")
            submitted = st.form_submit_button("✅ موافق")
            if submitted and name and group:
                send_to_telegram(name, group)
                st.success(f"مرحباً {name}! تم تسجيلك بنجاح ✅")
                st.session_state["page"] = "chat"

        st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
import requests  # For sending message to Telegram

# Replace these with your actual bot token and chat ID
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

def send_to_telegram(name, group):
    message = f"👤 اسم الطالب: {name}\n👥 القروب: {group}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def show_welcome():
    st.markdown(
        """
        <style>
        .welcome-title {
            font-size: 48px;
            font-weight: 900;
            color: #2e86de;
            text-align: center;
            margin-top: 30px;
        }
        .welcome-subtitle {
            font-size: 22px;
            color: #34495e;
            text-align: center;
            margin-bottom: 30px;
        }
        .welcome-container {
            background: linear-gradient(135deg, #f9f9f9 0%, #d0e8f2 100%);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>

        <div class="welcome-container">
            <h1 class="welcome-title">🦷 Welcome to Dentistry Stage 4! 🦷</h1>
            <p class="welcome-subtitle">Your journey to becoming a dental expert starts here. Let’s learn, practice, and succeed together! 💪✨</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        "https://images.unsplash.com/photo-1588776814546-44ff6a7e8d3b?auto=format&fit=crop&w=900&q=80",
        caption="Your Journey Starts Here",
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### 📝 ادخل معلوماتك للبدء")

    name = st.text_input("اسمك")
    group = st.text_input("قروبك")

    if st.button("✅ موافق"):
        if name.strip() and group.strip():
            send_to_telegram(name, group)
            st.success("✅ تم الإرسال! اضغط على الزر أدناه للمتابعة.")
            st.session_state.welcome_shown = True
            st.experimental_rerun()
        else:
            st.warning("❗ الرجاء تعبئة كل الحقول قبل المتابعة.")
