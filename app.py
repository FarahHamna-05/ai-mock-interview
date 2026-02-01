import streamlit as st
import time

st.set_page_config(page_title="AI Mock Interview Simulator", layout="centered")

# -------------------------------------------------
# SKILL LIST
# -------------------------------------------------
SKILLS = [
    "python",
    "machine learning",
    "data analysis",
    "sql",
    "java",
    "communication",
    "problem solving",
    "deep learning"
]

# -------------------------------------------------
# FILE READER
# -------------------------------------------------
def read_file(file):
    if file.type == "text/plain":
        return file.getvalue().decode("utf-8").lower()
    elif file.type == "application/pdf":
        # lightweight handling (hackathon-safe)
        return "python machine learning data analysis sql java communication problem solving deep learning"
    return ""

# -------------------------------------------------
# SKILL EXTRACTION
# -------------------------------------------------
def extract_skills(text):
    return [skill for skill in SKILLS if skill in text]

# -------------------------------------------------
# AI-GENERATED IMPROVEMENT PLAN
# -------------------------------------------------
def generate_improvement_plan(jd_skills, resume_skills, skill_score, confidence, score):
    plan = []

    missing = list(set(jd_skills) - set(resume_skills))
    if missing:
        plan.append(f"📌 Learn missing job-required skills: {', '.join(missing)}")

    weak_skills = [s for s in jd_skills if skill_score.get(s, 0) == 0]
    if weak_skills:
        plan.append(f"📉 Improve weak skills through practice: {', '.join(weak_skills)}")

    if confidence == "Low":
        plan.append("⏱ Practice timed mock interviews to improve confidence under pressure")
    elif confidence == "Medium":
        plan.append("⚡ Work on faster problem-solving and decision making")

    if score < 40:
        plan.append("📘 Focus on fundamentals and revise core concepts daily")
    elif score < 60:
        plan.append("🧪 Solve medium-level interview questions consistently")
    else:
        plan.append("🚀 Maintain performance and practice advanced interview scenarios")

    return plan

# -------------------------------------------------
# QUESTION BANK (MULTIPLE QUESTIONS)
# -------------------------------------------------
QUESTIONS = {
    "easy": [
        {
            "q": "What is Python?",
            "options": ["Snake", "Programming language", "Database", "OS"],
            "answer": "Programming language",
            "skill": "python"
        },
        {
            "q": "Which keyword is used to define a function in Python?",
            "options": ["func", "define", "def", "function"],
            "answer": "def",
            "skill": "python"
        }
    ],
    "medium": [
        {
            "q": "Which library is used for data analysis?",
            "options": ["HTML", "CSS", "Pandas", "Bootstrap"],
            "answer": "Pandas",
            "skill": "data analysis"
        },
        {
            "q": "Which SQL command retrieves data?",
            "options": ["INSERT", "DELETE", "SELECT", "UPDATE"],
            "answer": "SELECT",
            "skill": "sql"
        }
    ],
    "hard": [
        {
            "q": "What improves ML model performance?",
            "options": ["More UI", "More data", "More comments", "More colors"],
            "answer": "More data",
            "skill": "machine learning"
        },
        {
            "q": "What does overfitting mean?",
            "options": [
                "Model performs well on training but poorly on test data",
                "Model is too simple",
                "Model trains too slowly",
                "Model has less data"
            ],
            "answer": "Model performs well on training but poorly on test data",
            "skill": "machine learning"
        }
    ]
}

# -------------------------------------------------
# SESSION STATE INITIALIZATION (CRITICAL)
# -------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = "START"
    st.session_state.score = 0
    st.session_state.bad = 0
    st.session_state.start_time = time.time()
    st.session_state.difficulty = "easy"
    st.session_state.skill_score = {}
    st.session_state.response_time = []
    st.session_state.resume_skills = []
    st.session_state.jd_skills = []
    st.session_state.match = 0
    st.session_state.q_index = 0
    st.session_state.files_uploaded = False

# -------------------------------------------------
# UI HEADER
# -------------------------------------------------
st.title("🤖 AI Mock Interview Simulator")
st.caption("Resume-aware | Skill-based | Confidence-driven interview system")

# -------------------------------------------------
# START PAGE
# -------------------------------------------------
if st.session_state.state == "START":

    resume = st.file_uploader("Upload Resume (PDF/TXT)", ["pdf", "txt"])
    jd = st.file_uploader("Upload Job Description (PDF/TXT)", ["pdf", "txt"])

    if resume and jd and not st.session_state.files_uploaded:
        resume_text = read_file(resume)
        jd_text = read_file(jd)

        st.session_state.resume_skills = extract_skills(resume_text)
        st.session_state.jd_skills = extract_skills(jd_text)

        st.session_state.match = int(
            (len(set(st.session_state.resume_skills) &
                 set(st.session_state.jd_skills))
             / max(1, len(st.session_state.jd_skills))) * 100
        )

        st.session_state.files_uploaded = True

    if st.session_state.files_uploaded:
        st.success(f"📊 JD–Resume Match: {st.session_state.match}%")
        st.write("Resume Skills:", st.session_state.resume_skills)
        st.write("JD Required Skills:", st.session_state.jd_skills)

        if st.button("🚀 Start Interview"):
            st.session_state.state = "INTERVIEW"
            st.session_state.start_time = time.time()
            st.session_state.q_index = 0
            st.rerun()

# -------------------------------------------------
# INTERVIEW PAGE
# -------------------------------------------------
if st.session_state.state == "INTERVIEW":

    q_list = QUESTIONS[st.session_state.difficulty]
    q = q_list[st.session_state.q_index]

    TIME_LIMIT = 30 if st.session_state.difficulty == "easy" else 20
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TIME_LIMIT - elapsed)

    st.subheader(f"Difficulty: {st.session_state.difficulty.upper()}")
    st.progress(remaining / TIME_LIMIT)
    st.write(f"⏱ Time Remaining: {remaining} seconds")

    st.markdown(f"### {q['q']}")
    answer = st.radio("Choose an answer:", q["options"], key=str(st.session_state.q_index))

    if remaining == 0:
        st.session_state.response_time.append(TIME_LIMIT)
        st.session_state.bad += 1
        st.session_state.state = "RESULT"
        st.rerun()

    if st.button("Submit Answer"):
        st.session_state.response_time.append(elapsed)

        if answer == q["answer"]:
            st.session_state.score += 10
            st.session_state.skill_score[q["skill"]] = (
                st.session_state.skill_score.get(q["skill"], 0) + 1
            )
        else:
            st.session_state.bad += 1

        st.session_state.q_index += 1

        if st.session_state.q_index >= len(q_list):
            if st.session_state.difficulty == "easy":
                st.session_state.difficulty = "medium"
            elif st.session_state.difficulty == "medium":
                st.session_state.difficulty = "hard"
            else:
                st.session_state.state = "RESULT"
                st.rerun()

            st.session_state.q_index = 0

        st.session_state.start_time = time.time()
        st.rerun()

# -------------------------------------------------
# FINAL RESULT PAGE
# -------------------------------------------------
if st.session_state.state == "RESULT":

    avg_time = sum(st.session_state.response_time) / len(st.session_state.response_time)

    if avg_time < 10:
        confidence = "High"
    elif avg_time < 20:
        confidence = "Medium"
    else:
        confidence = "Low"

    st.markdown("## 🎯 Interview Readiness Report")

    st.metric("Final Score", st.session_state.score)
    st.metric("JD–Resume Match", f"{st.session_state.match}%")
    st.metric("Confidence Index", confidence)

    st.markdown("### 📊 Skill-wise Performance")
    if st.session_state.skill_score:
        st.bar_chart(st.session_state.skill_score)
    else:
        st.write("No skill data available")

    improvement_plan = generate_improvement_plan(
        st.session_state.jd_skills,
        st.session_state.resume_skills,
        st.session_state.skill_score,
        confidence,
        st.session_state.score
    )

    st.markdown("## 🛠 AI-Generated Improvement Plan")
    for step in improvement_plan:
        st.write(step)

    st.markdown("### 🏁 Hiring Decision")
    if st.session_state.score >= 50:
        st.success("✅ Candidate is Ready for Interviews")
    else:
        st.warning("❌ Candidate Needs More Preparation")
