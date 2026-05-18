import streamlit as st
import ollama
from datetime import datetime

# ---------------- SESSION STATE ----------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Pipeline Debugger",
    layout="wide"
)

# ---------------- SIDEBAR ----------------

st.sidebar.title("⚙️ About")

st.sidebar.write(
    """
    AI-powered pipeline debugging assistant.

    Features:
    - Root cause analysis
    - Failure detection
    - Fix suggestions
    - Debugging checklist
    - Conversational log investigation
    """
)

# ---------------- MAIN TITLE ----------------

st.title("🚀 AI Pipeline Debugger")

st.write("Upload pipeline logs and let AI analyze failures.")

# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload log file",
    type=["txt", "log"]
)

# ---------------- MAIN LOGIC ----------------

if uploaded_file:

    # Read uploaded file
    log_content = uploaded_file.read().decode("utf-8")

    # ---------------- SEVERITY ----------------

    severity = "Low"

    if "ERROR" in log_content:
        severity = "High"

    st.warning(f"Detected Severity Level: {severity}")

    # ---------------- LOG PREVIEW ----------------

    st.subheader("📄 Log Preview")

    st.code(log_content[:2000], language="text")

    # ---------------- ANALYZE BUTTON ----------------

    if st.button("Analyze Logs"):

        with st.spinner("Analyzing logs..."):

            prompt = f"""
            You are an expert senior data engineer.

            Analyze this pipeline log carefully.

            Return response STRICTLY in this format:

            Root Cause:
            - concise explanation

            Business Impact:
            - concise explanation

            Suggested Fix:
            - concise explanation

            Debugging Checklist:
            - bullet points only

            Keep response professional and short.

            Pipeline Log:
            {log_content[:1000]}
            """

            response = ollama.chat(
                model="phi3",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result = response["message"]["content"]

            # ---------------- ANALYSIS OUTPUT ----------------

            sections = result.split("\n\n")

            st.subheader("🤖 AI Analysis")

            for section in sections:
                st.info(section)

            st.success("Analysis completed successfully!")

            # ---------------- TIMESTAMP ----------------

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.caption(f"Analysis generated at: {timestamp}")

            # ---------------- DOWNLOAD REPORT ----------------

            st.download_button(
                label="📥 Download RCA Report",
                data=result,
                file_name=f"pipeline_rca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

    # ---------------- CHAT WITH LOGS ----------------

    st.subheader("💬 Ask Questions About Logs")

    user_question = st.text_input(
        "Ask anything about the uploaded logs"
    )

    if user_question:

        # Save user question
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        with st.spinner("Thinking..."):

            # Build conversation context
            conversation = f"""
                You are a senior production data engineer helping debug ETL pipelines.

                Pipeline Log:
                {log_content[:1000]}

                Conversation History:
                """

            for chat in st.session_state.chat_history:
                    conversation += f"""
                    {chat['role']}: {chat['content']}
                    """

            conversation += """

                Rules:
                - Do NOT repeat previous responses
                - Answer ONLY the latest question
                - Keep answers concise
                - Be technical and practical
                - For SQL requests, return SQL only
                - For prevention questions, return bullet points
                """
            # LLM call
            chat_response = ollama.chat(
                model="gemma:2b",
                messages=[
                    {
                        "role": "user",
                        "content": conversation
                    }
                ]
            )

            answer = chat_response["message"]["content"]

            # Save assistant response
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

    # ---------------- DISPLAY CHAT ----------------

    for chat in st.session_state.chat_history:

        if chat["role"] == "user":
            st.markdown(f"🧑 **You:** {chat['content']}")

        else:
            st.markdown(f"🤖 **AI:** {chat['content']}")