import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

#OpenAI Client initialization
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Page configuration
st.set_page_config(page_title="AI Pipeline Debugger")

#Title
st.title("AI Pipeline Debugger")

st.write("Upload your pipeline logs and let AI analyze failures.")

uploaded_file = st.file_uploader("upload a log file", type=["txt", "log"])

if uploaded_file:
    #Read Log Content
    log_content = uploaded_file.read().decode("utf-8")
    #Show Log Preview
    st.subheader("Log Preview")

    st.code(log_content[:2000],language="text")  # Show first 2000 characters of the log

    #Analyze Button
    if st.button("Analyze"):

       with st.spinner("Analyzing pipeline logs..."):
    
            prompt = f"""
                You are a senior data engineer.

                Analyze this pipeline log.

                Provide:
                1. Root Cause
                2. Business Impact
                3. Suggested Fix
                4. Debugging Checklist

                Log:
                {log_content}
                """

            response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

            result = response.choices[0].message.content

            st.subheader("🤖 AI Analysis")

            st.write(result)