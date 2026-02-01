import streamlit as st
import time

st.set_page_config(page_title="AI Mock Interview", layout="centered")

# -----------------------------
# QUESTIONS DATABASE
# -----------------------------
QUESTIONS = {
    "easy": [
        ("What is Python?", "python"),
        ("What is a variable?", "variable")
    ],
    "medium": [
        ("Explain OOP concepts in Python.", "oop"),
        ("Difference between list and tuple?", "list")
    ],
    "hard": [
        ("Explain multithreading in Python.", "thread"),
        ("How does Python manage memory?", "memory")
    ]
}

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "state" not in st.session_state:
    st.session_state.state = "START"
    st.session_state.score = 0
    st.session_state.bad_answers = 0
    st.session_state.difficulty = "easy"
    st.session_state.q_index = 0
    st.session_state.start_time = 0
    st.session_state.history = []

# -----------------------------
# TITLE
# -----------------------------
st.title("🤖 AI-Powered Mock Interview Platform")
st.caption("State-Based Adaptive Interview Simulation")

# -----------------------------
# START STATE
# -----------------------------
if st.session_state.state == "START":
    st.subheader("📄 Resume & Job Description")
    resume = st.text_area("Paste Resume Text")
    jd = st.text_area("Paste Job Description")

    if st.button("Start Interview"):
        st.session_state.state = "INTERVIEW"
        st.session_state.start_time = time.time()
        st.rerun()

# -----------------------------
# INTERVIEW STATE
# -----------------------------
if st.session_state.state == "INTERVIEW":

    questions = QUESTIONS[st.session_state.difficulty]

    if st.session_state.q_index >= len(questions):
        st.session_state.state = "END"
        st.rerun()

    question, keyword = questions[st.session_state.q_index]

    st.subheader(f"Difficulty: {st.session_state.difficulty.upper()}")
    st.write(f"🧠 Question: {question}")

    answer = st.text_area("✍️ Your Answer")

    TIME_LIMIT = 60
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TIME_LIMIT - elapsed)

    st.write(f"⏱ Time Remaining: {remaining} seconds")

    # -----------------------------
    # TIME EXCEEDED
    # -----------------------------
    if elapsed > TIME_LIMIT:
        st.warning("⛔ Time exceeded! Penalty applied.")
        st.session_state.bad_answers += 1
        st.session_state.q_index += 1
        st.session_state.start_time = time.time()

        if st.session_state.bad_answers >= 2:
            st.session_state.state = "TERMINATED"

        st.experimental_rerun()

    # -----------------------------
    # SUBMIT ANSWER
    # -----------------------------
    if st.button("Submit Answer"):
        score = 0

        # Objective scoring rules
        if len(answer.strip()) > 20:
            score += 40
        if keyword.lower() in answer.lower():
            score += 40
        if elapsed < 40:
            score += 20

        st.session_state.score += score
        st.session_state.history.append(score)

        # Difficulty adaptation
        if score >= 70:
            if st.session_state.difficulty == "easy":
                st.session_state.difficulty = "medium"
            elif st.session_state.difficulty == "medium":
                st.session_state.difficulty = "hard"
        else:
            st.session_state.bad_answers += 1

        # Early termination logic
        if st.session_state.bad_answers >= 2:
            st.session_state.state = "TERMINATED"
            st.rerun()

        st.session_state.q_index += 1
        st.session_state.start_time = time.time()
        st.rerun()

# -----------------------------
# TERMINATED STATE
# -----------------------------
if st.session_state.state == "TERMINATED":
    st.error("🚫 Interview Terminated Early")
    st.write("Reason: Poor performance or time violations")
    st.write(f"Final Score: **{st.session_state.score}**")

# -----------------------------
# END STATE
# --------------
