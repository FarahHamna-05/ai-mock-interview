import streamlit as st
import time
from io import StringIO

st.set_page_config(page_title="AI Mock Interview", layout="centered")

# ---------------------------------
# SKILL LIST
# ---------------------------------
SKILLS = [
    "python", "machine learning", "data analysis",
    "sql", "java", "communication",
    "problem solving", "deep learning"
]

# ---------------------------------
# READ FILE
# ---------------------------------
def read_file(file):
    if file.type == "text/plain":
        return file.getvalue().decode("utf-8").lower()
    elif file.type == "application/pdf":
        return "pdf uploaded"
    return ""

# ---------------------------------
# SKILL EXTRACTION
# ---------------------------------
def extract_skills(text):
    return [skill for skill in SKILLS if skill in text]

# ---------------------------------
# QUESTIONS WITH SKILLS
# ---------------------------------
QUESTIONS = {
    "easy": [{
        "q": "What is Python?",
        "options": ["Snake", "Programming language", "Database", "OS"],
        "answer": "Programming language",
        "skill": "python"
    }],
    "medium": [{
        "q": "Which is used for data analysis?",
        "options": ["HTML", "CSS", "Pandas", "Bootstrap"],
        "answer": "Pandas",
        "skill": "data analysis"
    }],
    "hard": [{
        "q": "What improves model performance?",
        "options": ["More data", "More UI", "More colors", "More comments"],
        "answer": "More data",
        "skill": "machine learning"
    }]
}

# ---------------------------------
# SESSION STATE
# ---------------------------------
if "state" not in st.session_state:
    st.session_state.state = "START"
    st.session_state.score = 0
    st.session_state.bad = 0
    st.session_state.start_time = time.time()
    st.session_state.difficulty = "easy"
    st.session_state.skill_score = {}
    st.session_state.response_time = []

# ---------------------------------
# TITLE
# ---------------------------------
st.title("🤖 AI Mock Interview Simulator")

# ---------------------------------
# START PAGE
# ---------------------------------
if st.session_state.state == "START":
    resume = st.file_uploader("Upload Resume", ["txt", "pdf"])
    jd = st.file_uploader("Upload Job Description", ["txt", "pdf"])

    if resume and jd:
        resume_text = read_file(resume)
        jd_text = read_file(jd)

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        match = int((len(set(resume_skills) & set(jd_skills)) / max(1, len(jd_skills))) * 100)

        st.success(f"📊 JD–Resume Match: {match}%")
        st.write("**Resume Skills:**", resume_skills)
        st.write("**JD Required Skills:**", jd_skills)

        if st.button("Start Interview"):
            st.session_state.state = "INTERVIEW"
            st.session_state.start_time = time.time()
            st.rerun()

# ---------------------------------
# INTERVIEW
# ---------------------------------
if st.session_state.state == "INTERVIEW":
    q = QUESTIONS[st.session_state.difficulty][0]

    LIMIT = 30 if st.session_state.difficulty == "easy" else 20
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = LIMIT - elapsed

    st.write(f"⏱ Time Left: {remaining}s")
    st.markdown(f"### {q['q']}")

    ans = st.radio("Choose:", q["options"])

    if remaining <= 0:
        st.session_state.bad += 1
        st.session_state.response_time.append(LIMIT)
        st.session_state.state = "RESULT"
        st.rerun()

    if st.button("Submit"):
        response_time = elapsed
        st.session_state.response_time.append(response_time)

        if ans == q["answer"]:
            st.session_state.score += 20
            st.session_state.skill_score[q["skill"]] = st.session_state.skill_score.get(q["skill"], 0) + 1
        else:
            st.session_state.bad += 1

        st.session_state.state = "RESULT"
        st.rerun()

# ---------------------------------
# FINAL RESULT
# ---------------------------------
if st.session_state.state == "RESULT":
    avg_time = sum(st.session_state.response_time) / len(st.session_state.response_time)

    if avg_time < 10:
        confidence = "High"
    elif avg_time < 20:
        confidence = "Medium"
    else:
        confidence = "Low"

    st.markdown("## 🎯 Final Interview Report")

    st.metric("Final Score", st.session_state.score)
    st.metric("Confidence Index", confidence)

    st.markdown("### 📊 Skill-wise Performance")
    st.bar_chart(st.session_state.skill_score)

    if st.session_state.score >= 60:
        st.success("✅ Ready for Interview")
    else:
        st.warning("❌ Needs Improvement")
def generate_improvement_plan(jd_skills, resume_skills, skill_score, confidence, score):
    plan = []

    # Missing skills
    missing = list(set(jd_skills) - set(resume_skills))
    if missing:
        plan.append(f"📌 Learn missing job-required skills: {', '.join(missing)}")

    # Weak skills
    weak_skills = [s for s in jd_skills if skill_score.get(s, 0) == 0]
    if weak_skills:
        plan.append(f"📉 Improve weak skills through practice: {', '.join(weak_skills)}")

    # Confidence-based suggestions
    if confidence == "Low":
        plan.append("⏱ Practice timed mock interviews to improve confidence under pressure")
    elif confidence == "Medium":
        plan.append("⚡ Work on faster problem-solving and decision making")

    improvement_plan = generate_improvement_plan(
    jd_skills,
    resume_skills,
    st.session_state.skill_score,
    confidence,
    st.session_state.score
)

st.markdown("## 🛠 AI-Generated Improvement Plan")
for step in improvement_plan:
    st.write(step)


    # Score-based guidance
    if score < 40:
        plan.append("📘 Focus on fundamentals and revise core concepts daily")
    elif score < 60:
        plan.append("🧪 Solve medium-level interview questions consistently")
    else:
        plan.append("🚀 Maintain performance and practice advanced interview scenarios")

    return plan
