import streamlit as st
import os
import json

st.set_page_config(page_title="LC Modular Learning", layout="wide")

MODULES_FOLDER = "modules"
DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# ---------------- SESSION INIT ----------------
if "started" not in st.session_state:
    st.session_state.started = False

st.title("📚 Laguna College Modular Learning System")

# ---------------- LOGIN ----------------
if not st.session_state.started:

    role = st.selectbox("Login as:", ["Student", "Teacher"])
    name = st.text_input("Enter your full name")

    if st.button("Enter System") and name:
        st.session_state.clear()
        st.session_state.started = True
        st.session_state.name = name
        st.session_state.role = role
        st.session_state.card_index = 0
        st.rerun()

# ---------------- TEACHER DASHBOARD ----------------
if st.session_state.started and st.session_state.role == "Teacher":

    st.header(f"👩‍🏫 Teacher Dashboard — {st.session_state.name}")

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]

    if not files:
        st.write("No student data yet.")
    else:
        for file in files:
            student_name = file.replace(".json", "")
            st.subheader(f"👤 {student_name}")

            with open(os.path.join(DATA_FOLDER, file), "r") as f:
                progress = json.load(f)

            completed = sum(progress.values())
            total = len(progress)

            if total > 0:
                percent = int((completed / total) * 100)
                st.progress(percent / 100)
                st.write(f"{percent}% completed")
            st.write(progress)

# ---------------- STUDENT LEARNING SYSTEM ----------------
if st.session_state.started and st.session_state.role == "Student":

    name = st.session_state.name
    student_file = os.path.join(DATA_FOLDER, f"{name}.json")

    if os.path.exists(student_file):
        with open(student_file, "r") as f:
            progress = json.load(f)
    else:
        progress = {}

    def save_progress():
        with open(student_file, "w") as f:
            json.dump(progress, f)

    def list_subjects():
        return [
            d for d in os.listdir(MODULES_FOLDER)
            if os.path.isdir(os.path.join(MODULES_FOLDER, d))
        ]

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

    # ---------- SUBJECT / LESSON ----------
    subjects = list_subjects()
    subject = st.sidebar.selectbox("Select Subject", subjects)

    lessons = list_lessons(subject)
    lesson = st.sidebar.selectbox("Select Lesson", lessons)

    lesson_id = f"{subject}-{lesson}"

    if lesson_id not in progress:
        progress[lesson_id] = False

    lesson_path = os.path.join(MODULES_FOLDER, subject, lesson)

    with open(lesson_path, "r", encoding="utf-8") as file:
        content = file.read()

    cards, quiz = parse_lesson(content)

    index = st.session_state.card_index
    total_cards = len(cards)

    st.markdown(f"### Card {index+1} of {total_cards}")

    card_type, card_content = cards[index]

    if card_type == "text":
        st.write(card_content)
    elif card_type == "image":
        st.image(card_content)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Previous") and index > 0:
            st.session_state.card_index -= 1
            st.rerun()

    with col2:
        if st.button("Next ➡️") and index < total_cards - 1:
            st.session_state.card_index += 1
            st.rerun()

    # ---------- QUIZ ----------
    if index == total_cards - 1 and quiz:
        st.markdown("---")
        question, options, answer = quiz
        choice = st.radio(question, options)
        if st.button("Submit Answer"):
            if choice.startswith(answer):
                st.success("Correct! Lesson completed.")
                progress[lesson_id] = True
                save_progress()
            else:
                st.error("Try again.")

    # ---------- PROGRESS ----------
    st.sidebar.markdown("## 📊 Your Progress")
    completed = sum(progress.values())
    total = len(progress)

    if total > 0:
        percent = int((completed / total) * 100)
        st.sidebar.progress(percent / 100)
        st.sidebar.write(f"{percent}% lessons completed")
