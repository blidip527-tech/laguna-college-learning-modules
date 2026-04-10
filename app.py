import streamlit as st
import os

st.set_page_config(page_title="Learning Modules", layout="wide")

MODULES_FOLDER = "modules"

ACCESS_CODES = {
    "STUD123": "student",
    "TEACH123": "teacher",
}

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

if st.sidebar.button("Logout"):
    st.session_state.role = None
    st.rerun()

# ---------- FUNCTIONS ----------
def list_subjects():
    return [d for d in os.listdir(MODULES_FOLDER) if os.path.isdir(os.path.join(MODULES_FOLDER, d))]

def list_lessons(subject):
    subject_path = os.path.join(MODULES_FOLDER, subject)
    return [f for f in os.listdir(subject_path) if f.endswith(".txt")]

def display_cards(content):
    cards = content.split("\n\n")
    for card in cards:
        st.markdown(f"""
        <div style='padding:15px;margin:10px 0;border-radius:10px;
        border:1px solid #ddd;background-color:#f9f9f9'>
        {card}
        </div>
        """, unsafe_allow_html=True)

# ---------- TEACHER PANEL ----------
if role == "teacher":
    st.sidebar.header("👩‍🏫 Teacher Panel")

    new_subject = st.sidebar.text_input("New Subject")
    if st.sidebar.button("Create Subject"):
        os.makedirs(os.path.join(MODULES_FOLDER, new_subject), exist_ok=True)
        st.sidebar.success("Subject created")

    subjects = list_subjects()
    if subjects:
        subject_choice = st.sidebar.selectbox("Select Subject", subjects)

        lesson_title = st.sidebar.text_input("Lesson Title")
        lesson_text = st.sidebar.text_area("Paste Lesson Content (separate ideas by blank lines)")

        if st.sidebar.button("Save Lesson"):
            filename = lesson_title.replace(" ", "_") + ".txt"
            lesson_path = os.path.join(MODULES_FOLDER, subject_choice, filename)
            with open(lesson_path, "w", encoding="utf-8") as f:
                f.write(lesson_text)
            st.sidebar.success("Lesson saved")

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
display_cards(content)
