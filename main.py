import streamlit as st
import os
import json
import tempfile
from langchain.document_loaders import PyPDFLoader

# ---------------- Safe import ----------------
try:
    from main_logic import get_response
except ModuleNotFoundError:
    st.error("Error: 'main_logic.py' not found in the current folder. Make sure it exists alongside this script.")
    get_response = None  # placeholder to avoid crashing

# ---------------- Helper Functions ----------------
def convert_into_dict(result):
    if isinstance(result, str):
        return json.loads(result)
    return result

def render_report(result):
    report = convert_into_dict(result)

    st.subheader("Match Score")
    score = int(report.get("match_score", 0))
    st.metric("Match Score", f"{score}/100")
    st.progress(max(0, min(score, 100)))

    st.subheader("Missing Skills")
    missing_skills = report.get("missing_skills", [])
    if missing_skills:
        for s in missing_skills:
            st.write(f"- {s}")

    st.subheader("Partially Covered Skills")
    partially_covered_skills = report.get("partially_covered_skills", [])
    if partially_covered_skills:
        for s in partially_covered_skills:
            st.write(f"- {s}")
    else:
        st.write("None")

    st.subheader("Recommendations")
    recommendations = report.get("recommendations", [])
    if recommendations:
        for r in recommendations:
            st.write(f"- {r}")

    st.subheader("Feedback")
    st.write(report.get("feedback", "No feedback provided."))

    with st.expander("View Full JSON Report", expanded=False):
        st.json(report)

    st.download_button(
        "Download JSON Report",
        data=json.dumps(report),
        file_name="report.json",
        mime="application/json",
        use_container_width=True
    )

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI Career Advisor", page_icon=":guardsman:", layout="wide")
st.title("🧠Career Advisor")
st.caption("Compare a candidate's Resume against a Job Description and get a structured skill-gap JSON report.")

with st.sidebar:
    st.header("Settings")
    st.markdown("Adjust the parameters for the AI model.")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
    max_tokens = st.slider("Max Tokens", 100, 2000, 1024)
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

# ---------------- Load Resume ----------------
resume = None
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    pdf_loader = PyPDFLoader(temp_file_path)
    resume = pdf_loader.load()

# ---------------- Job Description Input ----------------
jd = st.text_area(
    "Job Description",
    placeholder="Write the job description here...",
    width=800,
    height=300
)

# ---------------- Analyze Button ----------------
if st.button('Analyze'):
    with st.spinner("Analyzing..."):
        if not get_response:
            st.error("Cannot analyze resume because 'main_logic.py' is missing.")
        elif uploaded_file and jd:
            response = get_response(resume, jd, temperature, max_tokens)
            render_report(response)
        else:
            st.error("Please upload a resume and provide a job description.")




#--------- extra feature---------------#



#-----job search feature---#

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("gemini_api_key")

# Define the API endpoint
API_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions'

def get_job_skills(job_title):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    data = {
        'model': 'gemini-2.5-flash',
        'messages': [
            {'role': 'user', 'content': f"List the most important skills required to be a {job_title} in the current job market. Include technical and soft skills."}
        ],
        'temperature': 0.7
    }
    response = requests.post(API_URL, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

st.title("🛠️Job Skills Bot")
st.caption("Get the most important skills for any job title.")

job_name = st.text_input("Write the job title")

if st.button("Get Required Skills") and job_name:
    skills = get_job_skills(job_name)
    st.write(skills)  