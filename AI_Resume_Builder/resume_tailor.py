import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit UI
st.set_page_config(page_title="AI Resume Tailor", page_icon="🤖", layout="centered")
st.title("🤖 AI Resume Tailor")
st.write("Automatically tailor your résumé to any job description using AI.")

# Inputs
resume_text = st.text_area("Paste your Resume Text:", height=200, placeholder="Paste your current résumé here...")
job_description = st.text_area("Paste Job Description:", height=200, placeholder="Paste the job posting here...")

if st.button("✨ Generate Tailored Resume"):
    if not resume_text or not job_description:
        st.warning("Please provide both résumé and job description!")
    else:
        with st.spinner("AI is tailoring your résumé..."):
            prompt = f"""
            You are an expert AI career assistant.
            Rewrite the following résumé bullet points so they better match the job description below.
            Keep the structure professional and ATS-friendly.

            Resume:
            {resume_text}

            Job Description:
            {job_description}
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
            )

            tailored_resume = response.choices[0].message.content
            st.subheader("🎯 AI-Tailored Résumé:")
            st.write(tailored_resume)
            st.download_button("⬇️ Download Tailored Résumé", tailored_resume, file_name="AI_Tailored_Resume.txt")
