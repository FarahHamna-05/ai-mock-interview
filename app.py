import streamlit as st
import time

st.set_page_config(page_title="AI Mock Interview", layout="centered")

# ---------------------------------
# MCQ QUESTION BANK
# ---------------------------------
QUESTIONS = {
    "easy": [
        {
            "q": "What is Python?",
            "options": [
                "A snake",
                "A programming language",
                "A database",
                "An operating system"
            ],
            "answer": "A programming language"
        }
    ],
    "medium": [
        {
            "q": "Which concept allows creating multiple objects from a class?",
            "options": [
                "Inheritance",
                "Encapsulation",
                "Polymorphism",
                "Instantiation"
            ],
            "answer": "Instantiation"
        }
    ],
    "hard": [
        {
            "q": "What does multithreading improve in a program?",
            "options": [
                "Memory usage",
                "Execution speed",
                "Code readability",
                "Syntax correctness"
            ],
            "answer": "Execution speed"
        }
    ]
}

# ---------------------------------
# SESSION STATE
# ---------------------------------
if "state" not in st.session_state:
    st.session_state.state = "START"
    st.session_state.score = 0
    st.session_state.bad = 0
    st.session_state.difficulty = "easy"
    st.session_state.q_index = 0
    st.session_state.start_time = time.time()

# ---------------------------------
# TITLE
# ---------------------------------
st.title("🤖 AI-Powered Mock Interview")
st.caption("State-Based Interview with Adaptive Pressure")

# ---------------------------------
# START PAGE
# ---------------------------------
if st.session_state.state == "START":
    st.subheader("📄 Resume & Job Description")
    st.text_area("Paste Resume Text")
    st.text_area("Paste Job Description")

    if st.button("🚀 Start Interview"):
        st.session_state.state = "INTERVIEW"
        st.session_state.start_time = time.time()
        st.rerun()

# ---------------------------------
# INTERVIEW PAGE
# ---------------------------------
if st.session_state.state == "INTERVIEW":

    qset = QUESTIONS[st.session_state.difficulty]
    question = qset[st.session_state.q_index]

    TIME_LIMIT = 30
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TIME_LIMIT - elapsed)

    st.subheader(f"Difficulty: {st.session_state.difficulty.upper()}")
    st.progress(remaining / TIME_LIMIT)
    st.write(f"⏱ Time Remaining: **{remaining} seconds**")

    st.markdown(f"### 🧠 {question['q']}")

    choice = st.radio(
        "Choose your answer:",
        question["options"],
        key="mcq"
    )

    # TIME OVER
    if remaining == 0:
        st.warning("⛔ Time Up!")
        st.session_state.bad += 1
        st.session_state.q_index = 0
        st.session_state.start_time = time.time()

        if st.session_state.bad >= 2:
            st.session_state.state = "TERMINATED"

        st.rerun()

    # SUBMIT
    if st.button("Submit Answer"):
        if choice == question["answer"]:
            st.success("✅ Correct Answer")
            st.session_state.score += 20

            # Increase difficulty
            if st.session_state.difficulty == "easy":
                st.session_state.difficulty = "medium"
            elif st.session_state.difficulty == "medium":
                st.session_state.difficulty = "hard"
        else:
            st.error("❌ Wrong Answer")
            st.session_state.bad += 1

        if st.session_state.bad >= 2:
            st.session_state.state = "TERMINATED"
            st.rerun()

        st.session_state.start_time = time.time()
        st.rerun()

# ---------------------------------
# TERMINATED PAGE
# ---------------------------------
if st.session_state.state == "TERMINATED":
    st.error("🚫 Interview Terminated Early")
    st.write("Reason: Poor performance under pressure")
    st.write(f"### Final Score: {st.session_state.score}")

# ---------------------------------
# FINAL RESULT PAGE
# ---------------------------------
if st.session_state.score >= 60:
    readiness = "Strong"
    emoji = "🔥"
elif st.session_state.score >= 40:
    readiness = "Average"
    emoji = "⚠️"
else:
    readiness = "Needs Improvement"
    emoji = "❌"

if st.session_state.state in ["TERMINATED"] or st.session_state.score >= 60:

    st.markdown("---")
    st.markdown("## 🎯 Interview Readiness Report")

    st.metric(
        label="Final Score",
        value=f"{st.session_state.score} / 100",
        delta=readiness
    )

    st.progress(st.session_state.score / 100)

    st.markdown(f"### {emoji} Status: **{readiness}**")

    st.markdown("### 🧠 Performance Insights")
    if readiness == "Strong":
        st.write("✔ Strong fundamentals")
        st.write("✔ Handles pressure well")
    elif readiness == "Average":
        st.write("✔ Basic understanding")
        st.write("✖ Needs better consistency")
    else:
        st.write("✖ Weak fundamentals")
        st.write("✖ Poor time management")

    st.markdown("### 🏁 Hiring Decision")
    if readiness == "Strong":
        st.success("✅ Ready for Technical Interviews")
    else:
        st.warning("❌ Not Ready for This Role Yet")
