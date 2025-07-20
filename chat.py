import streamlit as st
import os
import uuid
from datetime import datetime, timedelta
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# إعداد المسارات وقاعدة البيانات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'chat.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# النماذج
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    profile_picture = Column(String(255), nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, default=True)
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    image_filename = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="messages")

Base.metadata.create_all(bind=engine)

# دوال مساعدة
def save_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((800, 800))
    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join(UPLOAD_DIR, filename)
    img.save(path, "JPEG", quality=85)
    return filename

def get_user_by_username(db, username):
    return db.query(User).filter(User.username == username).first()

def add_or_update_user(db, username, profile_picture_file=None):
    user = get_user_by_username(db, username)
    if not user:
        user = User(username=username)
        if profile_picture_file:
            user.profile_picture = save_image(profile_picture_file)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_seen = datetime.utcnow()
        user.is_online = True
        if profile_picture_file:
            user.profile_picture = save_image(profile_picture_file)
        db.commit()
    return user

def mark_user_offline(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_online = False
        db.commit()

def add_message(db, user_id, content, image_file=None):
    msg = Message(user_id=user_id, content=content)
    if image_file:
        msg.image_filename = save_image(image_file)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_recent_messages(db, limit=100):
    return db.query(Message).order_by(Message.timestamp.asc()).limit(limit).all()

def get_online_users(db, timeout_seconds=60):
    threshold = datetime.utcnow() - timedelta(seconds=timeout_seconds)
    return db.query(User).filter(User.last_seen >= threshold, User.is_online == True).all()

# الدالة الرئيسية المتوافقة مع run.py
def main():
    db = SessionLocal()

    if "visitor_name" not in st.session_state:
        st.warning("يرجى تسجيل الدخول أولاً.")
        st.session_state.page = "orders"
        st.rerun()

    username = st.session_state.visitor_name
    group = st.session_state.visitor_group

    user = add_or_update_user(db, username)
    st.session_state.user_id = user.id
    st.session_state.username = user.username

    st.title("💬 غرفة الدردشة")
    st.markdown(f"👋 مرحباً {username} ({group})")

    # الشريط الجانبي - المستخدمون المتصلون
    with st.sidebar:
        st.subheader("🟢 المتصلون حالياً")
        online_users = get_online_users(db)
        for u in online_users:
            st.markdown(f"- {u.username}")
        if st.button("🔙 العودة للصفحة الرئيسية"):
            st.session_state.page = "orders"
            st.rerun()

    # عرض الرسائل
    messages = get_recent_messages(db, limit=100)
    for msg in messages:
        cols = st.columns([1, 10])
        with cols[0]:
            st.markdown("👤")
        with cols[1]:
            timestamp_str = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            user_label = msg.user.username
            if msg.user.id == st.session_state.user_id:
                user_label += " (أنت)"
            st.markdown(f"**{user_label}**  *{timestamp_str}*")
            if msg.content:
                st.markdown(msg.content)
            if msg.image_filename:
                st.image(os.path.join(UPLOAD_DIR, msg.image_filename))
            st.markdown("---")

    # إرسال رسالة
    with st.form("send_message_form", clear_on_submit=True):
        message_text = st.text_area("اكتب رسالتك هنا...", height=80)
        message_image = st.file_uploader("📎 صورة (اختياري)", type=["png", "jpg", "jpeg", "webp", "gif"])
        submit = st.form_submit_button("📩 إرسال")
        if submit:
            if not message_text.strip() and not message_image:
                st.warning("يرجى كتابة رسالة أو إرفاق صورة.")
            else:
                add_message(db, user.id, message_text.strip(), message_image)
                st.rerun()
