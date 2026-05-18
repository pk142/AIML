# 🚀 AI Pipeline Debugger

An AI-powered operational debugging assistant built using Python, Streamlit, Ollama, and local LLMs to automate ETL and data pipeline failure analysis.

---

# 📌 Overview

AI Pipeline Debugger helps data engineers analyze pipeline logs, detect probable root causes, generate debugging suggestions, and interactively investigate failures using conversational AI.

The project uses locally running LLMs through Ollama, enabling fully offline AI-powered troubleshooting without relying on paid APIs.

---

# ✨ Features

- AI-powered Root Cause Analysis (RCA)
- Pipeline failure detection
- Severity identification
- Conversational Q&A over logs
- Downloadable RCA reports
- Multi-model architecture using local LLMs
- Streamlit-based interactive dashboard
- Offline inference using Ollama

---

# 🛠 Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| LLM Runtime | Ollama |
| RCA Model | Phi-3 |
| Chat/Q&A Model | Gemma 2B |

---

# 🔄 Workflow

Upload Logs
↓
AI Analysis (Phi3)
↓
Structured RCA
↓
Conversational Q&A (Gemma)
↓
Downloadable RCA Report

---

# 🧠 AI Engineering Concepts Used

- Local LLM inference
- Prompt engineering
- Multi-model architecture
- Conversational AI
- AI-assisted operational troubleshooting
- Context-aware log analysis
- Streamlit AI app development

---

# 🚀 Future Enhancements

- Vector database integration
- RAG-based log retrieval
- Airflow API integration
- Real-time monitoring
- Multi-user support
- LLM observability dashboard

---

# ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py