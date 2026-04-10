import streamlit as st
import os

st.set_page_config(page_title="Learning Modules", layout="wide")

MODULES_FOLDER = "modules"

# 🔑 ACCESS CODES (you edit these)
ACCESS_CODES = {
    "STUD123": "student",
    "STUD456": "student",
    "TEACH123": "teacher",
}

# Ensure modules folder exists
if not os.path.exists(MODULES_FOLDER):
    os.makedirs(MODULES_FOLDER)

# ---------- LOGIN ----------
st.title("📚 Laguna College Learning Modules")

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    code = st.text_input("Enter Access Code", type="password")
    if st.button("Login"):
        if code in ACCESS_CODES:
            st.session_state.role = ACCESS_CODES[code]
            st.success(f"Logged in as {st.session_state.role}")
        else:
            st.error("Invalid code")
    st.stop()

role = st.session_state.role

# ---------- FUNCTIONS ----------
def list_subjects():
    return [d for d in os.listdir(MODULES_FOLDER) if os.path.isdir(os.path.join(MODULES_FOLDER, d))]

def list_lessons(subject):
    subject_path = os.path.join(MODULES_FOLDER, subject)
    return [f for f in os.listdir(subject_path) if f.endswith(".txt")]

# ---------- TEACHER PANEL ----------
if role == "teacher":
    st.sidebar.header("👩‍🏫 Teacher Panel")

    new_subject = st.sidebar.text_input("Create New Subject")
    if st.sidebar.button("Add Subject"):
        os.makedirs(os.path.join(MODULES_FOLDER, new_subject), exist_ok=True)
        st.sidebar.success("Subject created")

    subject_choice = st.sidebar.selectbox("Select Subject", list_subjects())

    uploaded_file = st.sidebar.file_uploader("Upload Lesson (.txt)", type="txt")
    if uploaded_file:
        lesson_path = os.path.join(MODULES_FOLDER, subject_choice, uploaded_file.name)
        with open(lesson_path, "wb") as f:
            f.write(uploaded_file.read())
        st.sidebar.success("Lesson uploaded")

# ---------- STUDENT VIEW ----------
st.sidebar.header("📖 Lessons")

subjects = list_subjects()
subject = st.sidebar.selectbox("Select Subject", subjects)

lessons = list_lessons(subject)
lesson = st.sidebar.selectbox("Select Lesson", lessons)

lesson_path = os.path.join(MODULES_FOLDER, subject, lesson)

with open(lesson_path, "r", encoding="utf-8") as file:
    content = file.read()

st.markdown(f"## {lesson.replace('.txt','')}")
st.write(content)
