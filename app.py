import streamlit as st
import time
import openai
import random

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="AI Mock Interview", layout="centered")
st.title("🤖 AI-Powered Mock Interview Platform")

st.markdown("""
Upload your **Resume** and **Job Description**, answer timed MCQs, and get a readiness score with feedback.
""")

SKILLS = ["Python", "SQL", "Machine Learning", "React", "Data Analysis", "Java"]

# -------------------------
# GPT Setup
# -------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in SKILLS if skill.lower() in text]

def generate_mcqs(skills, num_questions=3):
    prompt = f"""
Generate {num_questions} multiple-choice questions with 4 options each based on these skills: {skills}.
Return as a Python list of dicts with 'question', 'options', 'answer' keys.
"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        import ast
        mcqs = ast.literal_eval(response.choices[0].text.strip())
        return mcqs
    except:
        # fallback demo questions
        return [
            {'question': 'Which Python data type is immutable?', 
             'options': ['List', 'Tuple', 'Set', 'Dictionary'], 
             'answer': 'B'},
            {'question': 'Which SQL statement is used to extract data?', 
             'options': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'], 
             'answer': 'A'},
            {'question': 'Which algorithm is supervised ML?', 
             'options': ['K-Means', 'Decision Tree', 'DBSCAN', 'Apriori'], 
             'answer': 'B'}
        ]

def evaluate_answer_gpt(question, answer):
    prompt = f"""
You are an expert technical interviewer. Score this MCQ answer 0-20 for accuracy, clarity, depth, relevance.
Question: {question}
Answer: {answer}
Return only a number.
"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=5,
            temperature=0
        )
        return min(max(int(response.choices[0].text.strip()),0),20)
    except:
        return 10

def generate_feedback_gpt(question, answer):
    prompt = f"""
You are an expert career coach. Provide concise feedback for this answer.
Question: {question}
Answer: {answer}
Focus on strengths, weaknesses, and tips.
"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except:
        return "Practice improving clarity and depth."

# -------------------------
# File Upload
# -------------------------
resume_file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)")
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)")

if resume_file and jd_file:
    try:
        resume_text = resume_file.read().decode("utf-8", errors="ignore")
    except:
        resume_text = ""
    try:
        jd_text = jd_file.read().decode("utf-8", errors="ignore")
    except:
        jd_text = ""

    st.subheader("✅ Candidate Skills Detected")
    candidate_skills = extract_skills(resume_text)
    st.write(candidate_skills if candidate_skills else "No matching skills found.")

    # -------------------------
    # Generate MCQs
    # -------------------------
    st.subheader("📝 Interview Questions (MCQs)")
    mcqs = generate_mcqs(candidate_skills, num_questions=3)
    total_score = 0
    feedback = {}

    for i, mcq in enumerate(mcqs):
        st.write(f"**Q{i+1}: {mcq['question']}**")

        # Radio buttons
        selected_option = st.radio("Select your answer:", mcq['options'], key=f"q{i}")

        # Timer countdown
        timer_placeholder = st.empty()
        start_time = time.time()
        time_limit = 60
        elapsed = 0

        submit_button = st.button(f"Submit Q{i+1}", key=f"btn{i}")
        while elapsed < time_limit:
            remaining = time_limit - int(elapsed)
            timer_placeholder.markdown(f"⏱️ Time remaining: {remaining} seconds")
            time.sleep(1)
            elapsed = time.time() - start_time
            # If submit pressed, break early
            if submit_button:
                break

        if elapsed >= time_limit and not submit_button:
            st.warning("⏱️ Time is up! Answer will be scored as 0.")
            score = 0
        else:
            score = evaluate_answer_gpt(mcq['question'], selected_option)
        
        total_score += score
        feedback[f"Q{i+1} Feedback"] = generate_feedback_gpt(mcq['question'], selected_option)
        st.info(feedback[f"Q{i+1} Feedback"])
        timer_placeholder.empty()  # Clear timer

    # -------------------------
    # Final Readiness Score
    # -------------------------
    readiness_score = min(total_score * 100 // (len(mcqs)*20), 100)
    st.markdown("---")
    st.subheader("🏆 Final Interview Readiness Score")
    st.write(f"**{readiness_score}/100**")

    st.subheader("💡 Strengths & Weaknesses")
    st.markdown(f"""
    <div style='background-color:#f0f0f0; padding:10px; border-radius:10px'>
    <ul>
    <li>Technical Skills: Strong</li>
    <li>Problem Solving: Average</li>
    <li>Communication: Needs Improvement</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📌 Notes for Improvement")
    st.write("Focus on explaining your thought process, highlight relevant skills, and practice under timed conditions.")


