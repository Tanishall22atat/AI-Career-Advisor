from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
import os


def load_llm(temperature: 0.5, max_tokens: int = 1024):
    load_dotenv()
    groq_api_key = os.getenv('groq_api_key')
    os.environ['groq_api_key'] = groq_api_key
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        max_tokens=max_tokens
    )


#we use the system prompt
system_prompt = """
You are an **AI Career Advisor and Resume Analyzer** designed to give *precise, structured, and actionable* feedback.

🎯 **Objective:**
You will be provided two inputs:
1. **Job Description (JD)** – with role title, required skills, and responsibilities.
2. **Candidate Resume** – with education, skills, projects, certifications, and experience.

Your task is to:
- Parse both documents carefully.
- Compare the resume content against the JD requirements in detail.
- Output a structured JSON report with: match score, missing skills, partially covered skills, recommendations, and feedback.

---

📌 **Output Format (STRICT JSON ONLY, no explanations, no commentary, no markdown):**

{{
  "match_score": 72,
  "missing_skills": ["Kubernetes", "AWS Lambda"],
  "partially_covered_skills": ["Azure Functions"],
  "recommendations": [
    "Highlight cloud-native experience with AWS",
    "Add certification in Kubernetes or Docker",
    "Emphasize leadership experience in DevOps projects"
  ],
  "feedback": "Solid backend expertise but resume lacks emphasis on cloud-native and container orchestration."
}}

---

📌 **Detailed Instructions:**

1. **Match Score (0–100):**
   - Start at 100 and deduct based on gaps:
     - Each missing **critical technical skill**: -5 to -10 points.
     - Each missing **key responsibility / domain requirement**: -3 to -7 points.
     - Lack of alignment in experience vs. JD role level: -5 to -10 points.
   - Reward extra credit (+2–5) for additional highly relevant skills not in JD but useful.
   - Ensure scoring is **balanced and realistic** (not inflated).

2. **Missing Skills:**
   - List **critical hard skills explicitly mentioned in JD but absent in resume**.
   - Examples: Kubernetes, AWS Lambda, React, Terraform, Leadership, Stakeholder Management.
   - Only include skills that are truly absent.

3. **Partially Covered Skills:**
   - List skills that are **similar/related but not exact matches**.
   - Example: Resume has "Azure Functions" but JD asks "AWS Lambda".
   - Example: Resume has "CI/CD pipelines with GitHub Actions" but JD asks "Jenkins".
   - Helps candidate see near-misses they should emphasize or reframe.

4. **Recommendations (actionable):**
   - Always link directly to JD requirements.
   - Categories:
     - **Resume Edits:** Add missing keywords, rearrange sections, emphasize relevant projects.
     - **Skill Development:** Suggest specific certifications, training, or side projects.
     - **Experience Highlighting:** Recommend rephrasing existing experience to align with JD.
   - Keep them **specific, realistic, and measurable** (not vague).

5. **Feedback (short summary):**
   - 2–4 sentences max.
   - Tone: constructive + professional.
   - Highlight strengths + weaknesses.
   - Example: “Strong Java and Spring Boot background. Missing exposure to AWS cloud-native tools. Resume is detailed but lacks keywords from JD such as Kubernetes and Terraform.”

---

📌 **Additional Guidelines:**
- **STRICT JSON ONLY**: Do not include explanations, markdown, or commentary.
- **No hallucination**: Only extract from given JD and Resume.
- **Career Level Sensitivity**: If resume experience level does not align with JD seniority, mention in recommendations.
- **Soft Skills**: Include them only if JD explicitly lists them.
- **Consistency**: Keep field names lowercase with underscores.
- **Formatting**: Ensure valid JSON, no trailing commas, all strings double-quoted.

---

📌 **Context to Analyze:**
Job_Description:
{job_description}

Candidate_Resume:
{candidate_resume}
---
"""



def get_response(resume, jd, temperature, max_tokens):  #to get response, we need resume and jd both
    llm = load_llm(temperature, max_tokens)
    # prompt -> JD + Resume

    prompt = PromptTemplate(
        template=system_prompt,
        input_variables=["job_description", "candidate_resume"]
        )

    chain = prompt | llm | JsonOutputParser()   #we create chain of prompt, llm and output parser
    # invoke the chain with job description and resume
    # this will return a structured JSON report 

    return chain.invoke({
        "job_description": jd,
        "candidate_resume": resume
    })





import datetime
import random

class AvatarLogic:
    def __init__(self):
        self.mood = "neutral"  # default mood
        self.time_of_day = self.get_time_of_day()

    def get_time_of_day(self):
        """Determine time of day (morning/afternoon/evening/night)."""
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def set_mood(self, mood=None):
        """Set mood manually or randomly if none provided."""
        moods = ["happy", "sad", "excited", "tired", "neutral", "focused"]
        if mood and mood in moods:
            self.mood = mood
        else:
            self.mood = random.choice(moods)

    def get_avatar_expression(self):
        """Return avatar expression based on mood & time of day."""
        expressions = {
            "morning": "🌅 Fresh start of the day!",
            "afternoon": "☀️ Keep up the energy!",
            "evening": "🌇 Winding down, stay focused!",
            "night": "🌙 Time to relax soon..."
        }

        mood_responses = {
            "happy": "😊 Your avatar looks cheerful!",
            "sad": "😢 Your avatar looks a bit down.",
            "excited": "🤩 Your avatar is full of energy!",
            "tired": "🥱 Your avatar seems sleepy.",
            "neutral": "😐 Just neutral vibes.",
            "focused": "🎯 Your avatar is concentrating."
        }

        return f"{expressions[self.time_of_day]} | {mood_responses[self.mood]}"

    def update(self):
        """Update avatar state (can be called every few seconds)."""
        self.time_of_day = self.get_time_of_day()
        return self.get_avatar_expression()


import streamlit as st
from main_logic import AvatarLogic

# Initialize avatar
avatar = AvatarLogic()
avatar.set_mood()  # random mood
expression = avatar.update()

# Show on the website
st.sidebar.subheader("🧑‍💻 Your Coding Companion")
st.sidebar.write(expression)

