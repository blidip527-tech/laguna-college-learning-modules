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

def parse_lesson(content):
    lines = content.split("\n")
    cards = []
    quiz = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("[image:"):
            url = line.replace("[image:", "").replace("]", "").strip()
            cards.append(("image", url))

        elif line.startswith("QUESTION:"):
            question = line.replace("QUESTION:", "").strip()
            options = []
            answer = ""
            i += 1
            while i < len(lines) and lines[i].strip() != "":
                l = lines[i].strip()
                if l.startswith(("A.", "B.", "C.", "D.")):
                    options.append(l)
                if l.startswith("ANSWER:"):
                    answer = l.replace("ANSWER:", "").strip()
                i += 1
            quiz = (question, options, answer)

        elif line != "":
            cards.append(("text", line))

        i += 1

    return cards, quiz

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
        lesson_text = st.sidebar.text_area("Paste Lesson Content")

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

cards, quiz = parse_lesson(content)

# Track card position
if "card_index" not in st.session_state:
    st.session_state.card_index = 0

total_cards = len(cards)
index = st.session_state.card_index

st.markdown(f"### Card {index+1} of {total_cards}")

card_type, card_content = cards[index]

st.markdown("<div style='padding:20px;border-radius:12px;border:1px solid #ddd;background:#f9f9f9'>", unsafe_allow_html=True)

if card_type == "text":
    st.write(card_content)
elif card_type == "image":
    st.image(card_content)

st.markdown("</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Previous") and index > 0:
        st.session_state.card_index -= 1
        st.rerun()

with col2:
    if st.button("Next ➡️") and index < total_cards - 1:
        st.session_state.card_index += 1
        st.rerun()

# Show quiz only after last card
if index == total_cards - 1 and quiz:
    st.markdown("---")
    question, options, answer = quiz
    choice = st.radio(question, options)
    if st.button("Check Answer"):
        if choice.startswith(answer):
            st.success("Correct!")
        else:
            st.error("Try again.")
