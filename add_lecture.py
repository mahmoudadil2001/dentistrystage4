import streamlit as st
import os
import base64
import requests
import re

def load_lecture_titles(subject):
    titles_path = os.path.join(subject, "edit", "lecture_titles.py")
    if not os.path.exists(titles_path):
        return {}

    with open(titles_path, "r", encoding="utf-8") as f:
        content = f.read()

    namespace = {}
    exec(content, namespace)
    return namespace.get("lecture_titles", {})

def save_lecture_titles(subject, lecture_titles):
    titles_path = os.path.join(subject, "edit", "lecture_titles.py")
    if not os.path.exists(os.path.dirname(titles_path)):
        os.makedirs(os.path.dirname(titles_path))

    with open(titles_path, "w", encoding="utf-8") as f:
        f.write("lecture_titles = {\n")
        for k in sorted(lecture_titles.keys()):
            title = lecture_titles[k].replace('"', '\\"')
            f.write(f'    {k}: "{title}",\n')
        f.write("}\n")

    return titles_path

def push_to_github(file_path, commit_message, delete=False):
    token = st.secrets["GITHUB_TOKEN"]
    user = st.secrets["GITHUB_USER"]
    repo = st.secrets["GITHUB_REPO"]

    url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}"
    r = requests.get(url, headers={"Authorization": f"token {token}"})
    sha = r.json().get("sha") if r.status_code == 200 else None

    if delete:
        if not sha:
            return
        requests.delete(
            url,
            headers={"Authorization": f"token {token}"},
            json={"message": commit_message, "sha": sha, "branch": "main"}
        )
    else:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        data = {"message": commit_message, "content": content, "branch": "main"}
        if sha:
            data["sha"] = sha

        res = requests.put(url, headers={"Authorization": f"token {token}"}, json=data)

        if res.status_code not in [200, 201]:
            st.error(f"❌ خطأ في GitHub: {res.status_code}")
            st.json(res.json())

def get_existing_lectures(subject):
    lecture_files = os.listdir(subject) if os.path.exists(subject) else []
    lecture_dict = {}

    for f in lecture_files:
        match = re.match(rf"{subject}(\d+)(?:_v(\d+))?\.py$", f)
        if match:
            lec_num = int(match.group(1))
            version = int(match.group(2)) if match.group(2) else 1
            if lec_num not in lecture_dict:
                lecture_dict[lec_num] = []
            lecture_dict[lec_num].append((version, f))

    return lecture_dict

def add_lecture_page():
    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative",
        "oralpathology", "oralsurgery", "orthodontics", "pedodontics",
        "periodontology", "prosthodontics"
    ]

    tab1, tab2 = st.tabs(["➕ إضافة محاضرة", "🗑️ إدارة / حذف المحاضرات"])

    # ➕ إضافة محاضرة
    with tab1:
        st.header("➕ إضافة محاضرة")
        subject = st.selectbox("📌 اختر المادة", subjects, key="add_subject")

        if subject:
            if "step" not in st.session_state:
                st.session_state.step = 1
            if st.session_state.step == 1:
                if st.button("التالي: اختر العملية"):
                    st.session_state.step = 2

            if st.session_state.step >= 2:
                operation = st.radio("اختر العملية:", ("محاضرة جديدة", "نسخة جديدة"), key="add_operation")

                if st.session_state.step == 2 and operation:
                    if st.button("التالي: أدخل البيانات"):
                        st.session_state.step = 3
                        st.session_state.operation = operation

                if st.session_state.step == 3:
                    if st.session_state.operation == "محاضرة جديدة":
                        lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1, key="add_lec_num")
                        lec_title = st.text_input("عنوان المحاضرة (سيظهر في الواجهة)", key="add_lec_title")
                        content_code = st.text_area("اكتب كود الأسئلة (questions و Links)", height=300, key="add_code")

                        if st.button("✅ إضافة وحفظ", key="add_save_lecture"):
                            if not lec_title.strip():
                                st.error("❌ يجب كتابة عنوان المحاضرة")
                            elif not content_code.strip():
                                st.error("❌ يجب كتابة الكود")
                            else:
                                lecture_dict = get_existing_lectures(subject)
                                if lec_num in lecture_dict:
                                    st.error(f"❌ عذراً، المحاضرة رقم {lec_num} موجودة بالفعل!")
                                else:
                                    filename = f"{subject}{lec_num}.py"
                                    file_path = os.path.join(subject, filename)

                                    if not os.path.exists(subject):
                                        os.makedirs(subject)

                                    with open(file_path, "w", encoding="utf-8") as f:
                                        f.write(content_code)

                                    lecture_titles = load_lecture_titles(subject)
                                    lecture_titles[int(lec_num)] = lec_title.strip()
                                    titles_path = save_lecture_titles(subject, lecture_titles)

                                    push_to_github(file_path, f"Add lecture {filename}")
                                    push_to_github(titles_path, f"Update lecture titles for {subject}")

                                    st.success(f"✅ تم إنشاء الملف: {file_path}")
                                    st.info("📌 تم تحديث العنوان في lecture_titles.py ورفعه إلى GitHub ✅")
                                    st.session_state.step = 1  # للعودة للخطوة الأولى

                    elif st.session_state.operation == "نسخة جديدة":
                        lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1, key="add_ver_lec_num")
                        version_num = st.number_input("رقم النسخة", min_value=2, step=1, key="add_version_num")
                        content_code = st.text_area("اكتب كود الأسئلة (questions و Links)", height=300, key="add_ver_code")

                        if st.button("✅ إضافة وحفظ النسخة", key="add_save_version"):
                            lecture_dict = get_existing_lectures(subject)
                            versions = [v for v, _ in lecture_dict.get(lec_num, [])]

                            if version_num in versions:
                                st.error(f"❌ عذراً، النسخة رقم {version_num} من المحاضرة {lec_num} موجودة بالفعل!")
                            elif not content_code.strip():
                                st.error("❌ يجب كتابة الكود")
                            else:
                                filename = f"{subject}{lec_num}_v{version_num}.py"
                                file_path = os.path.join(subject, filename)

                                if not os.path.exists(subject):
                                    os.makedirs(subject)

                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(content_code)

                                push_to_github(file_path, f"Add version {version_num} for lecture {lec_num}")
                                st.success(f"✅ تم إنشاء النسخة: {file_path}")
                                st.session_state.step = 1  # للعودة للخطوة الأولى

    # 🗑️ إدارة / حذف المحاضرات
    with tab2:
        st.header("🗑️ إدارة / حذف المحاضرات")
        subject = st.selectbox("📌 اختر المادة", subjects, key="delete_subject")
        if subject:
            if "del_step" not in st.session_state:
                st.session_state.del_step = 1
            if st.session_state.del_step == 1:
                if st.button("التالي: اختر المحاضرة"):
                    st.session_state.del_step = 2

            if st.session_state.del_step >= 2:
                lecture_dict = get_existing_lectures(subject)
                lecture_titles = load_lecture_titles(subject)

                if not lecture_dict:
                    st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")
                else:
                    options = []
                    for lec_num in sorted(lecture_dict.keys()):
                        title = lecture_titles.get(lec_num, "بدون عنوان")
                        options.append(f"{lec_num} - {title}")

                    selected_option = st.selectbox("اختر محاضرة", options, key="delete_lecture_select")
                    selected_lec_num = int(selected_option.split(" - ")[0])

                    if st.session_state.del_step == 2 and selected_option:
                        if st.button("التالي: اختر النسخة للحذف"):
                            st.session_state.del_step = 3
                            st.session_state.selected_lec_num = selected_lec_num

                    if st.session_state.del_step == 3:
                        versions = sorted(lecture_dict[st.session_state.selected_lec_num], key=lambda x: x[0])
                        version_options = [f"نسخة {v[0]} - {v[1]}" for v in versions]

                        selected_version = st.selectbox("اختر النسخة لحذفها", version_options, key="delete_version_select")
                        selected_file = versions[version_options.index(selected_version)][1]

                        if st.button("❌ حذف النسخة المحددة", key="delete_button"):
                            file_path = os.path.join(subject, selected_file)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                push_to_github(file_path, f"Delete lecture {selected_file}", delete=True)
                                st.success("✅ تم حذف الملف")
                                st.session_state.del_step = 1
                                st.experimental_rerun()
                            else:
                                st.error("❌ الملف غير موجود للحذف")

if __name__ == "__main__":
    add_lecture_page()
