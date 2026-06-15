"""
Secure Document Intelligence — Streamlit Frontend
All requests go to the local FastAPI backend. No external API calls.
"""
import os
import requests
import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API = f"{BACKEND_URL}/api/v1"
TIMEOUT = 180  # seconds (LLM can be slow on CPU)

# ── Page setup ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Secure Document Intelligence",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] { background: #0f1117; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* Cards */
    .card {
        background: #1e2130;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }

    /* Source badge */
    .source-badge {
        display: inline-block;
        background: #2d3250;
        color: #7eb3ff;
        font-size: 0.78rem;
        padding: 2px 10px;
        border-radius: 20px;
        margin: 2px 4px 2px 0;
    }

    /* Answer box */
    .answer-box {
        background: #13151f;
        border-left: 4px solid #4a90d9;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        line-height: 1.7;
    }

    /* Security notice */
    .security-badge {
        background: #0d2a1e;
        border: 1px solid #1a5c3a;
        color: #4caf7d;
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        font-size: 0.82rem;
        margin-bottom: 1rem;
    }

    /* Score bar */
    .score-bar {
        height: 4px;
        border-radius: 2px;
        background: linear-gradient(90deg, #4a90d9, #6dd5a0);
        margin-top: 4px;
    }

    h1, h2, h3 { color: #e8eaf6 !important; }
    .stButton>button {
        background: #3d5afe;
        color: white;
        border: none;
        border-radius: 6px;
    }
    .stButton>button:hover { background: #5472ff; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────

def api_get(path: str):
    try:
        r = requests.get(f"{API}{path}", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is the server running?")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path: str, json_data=None, files=None):
    try:
        r = requests.post(f"{API}{path}", json=json_data, files=files, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return None
    except requests.HTTPError as e:
        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
        st.error(f"API error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_delete(path: str):
    try:
        r = requests.delete(f"{API}{path}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Delete error: {e}")
        return None


def render_sources(sources: list):
    if not sources:
        return
    st.markdown("**📎 Sources:**")
    for s in sources:
        score_pct = int(s.get("score", 0) * 100)
        with st.expander(
            f"📄 {s['source']}  ·  Page {s['page']}  ·  Relevance: {score_pct}%",
            expanded=False,
        ):
            st.markdown(f"> {s['excerpt']}")
            st.markdown(
                f'<div class="score-bar" style="width:{score_pct}%"></div>',
                unsafe_allow_html=True,
            )


# ── Session state defaults ─────────────────────────────────────────────────

if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "documents" not in st.session_state:
    st.session_state.documents = []


# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔒 Secure Doc Intel")
    st.markdown(
        '<div class="security-badge">🛡️ 100% local · No cloud API · No data egress</div>',
        unsafe_allow_html=True,
    )

    # Health check
    if st.button("⚡ Check System Health", use_container_width=True):
        health = api_get("/health")
        if health:
            status_icon = "✅" if health["status"] == "ok" else "⚠️"
            st.write(f"{status_icon} **Status:** {health['status']}")
            st.write(f"🗄️ **Qdrant:** {health['qdrant']}")
            st.write(f"🤖 **Ollama:** {health['ollama']}")
            st.write(f"📦 **LLM:** `{health['llm_model']}`")
            st.write(f"🔢 **Embed:** `{health['embed_model']}`")

    st.divider()

    # Document list
    st.markdown("### 📁 Uploaded Documents")
    if st.button("🔄 Refresh list", use_container_width=True):
        data = api_get("/documents")
        if data:
            st.session_state.documents = data["documents"]

    docs = st.session_state.documents
    if not docs:
        st.info("No documents yet. Upload one →")
    else:
        doc_options = {f"{d['filename']} ({d['chunks']} chunks)": d["doc_id"] for d in docs}
        doc_options["🌐 All documents"] = None

        selected_label = st.selectbox(
            "Query scope:",
            options=list(doc_options.keys()),
        )
        st.session_state.selected_doc = doc_options[selected_label]

        # Delete
        if st.session_state.selected_doc:
            if st.button("🗑️ Delete selected", use_container_width=True):
                res = api_delete(f"/documents/{st.session_state.selected_doc}")
                if res:
                    st.success(res["message"])
                    st.session_state.selected_doc = None
                    st.session_state.documents = []
                    st.rerun()

    st.divider()

    # Clear chat
    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ── Main content ───────────────────────────────────────────────────────────

st.title("🔒 Secure Document Intelligence")
st.caption("Upload documents · Ask questions · Get cited answers — entirely offline")

tab_upload, tab_chat, tab_summary = st.tabs(["📤 Upload", "💬 Ask Questions", "📋 Summary"])


# ──────────────────── UPLOAD TAB ────────────────────────────────────────────

with tab_upload:
    st.markdown("### Upload a Document")
    st.markdown(
        "Supported formats: **PDF**, **DOCX**, **TXT** · Max 50 MB · "
        "All processing is local — documents never leave this server."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "doc", "txt"],
        help="Your file is processed locally. No data is sent to any cloud service.",
    )

    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        with col2:
            if st.button("🚀 Ingest Document", use_container_width=True):
                with st.spinner("Extracting text, chunking, and building embeddings…"):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    result = api_post("/upload", files=files)

                if result:
                    st.success(f"✅ {result['message']}")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Chunks stored", result["chunks_stored"])
                    col_b.metric("Pages extracted", result["pages"])
                    col_c.metric("Doc ID", result["doc_id"][:8] + "…")

                    # Refresh documents list
                    data = api_get("/documents")
                    if data:
                        st.session_state.documents = data["documents"]


# ──────────────────── CHAT TAB ───────────────────────────────────────────────

with tab_chat:
    st.markdown("### Ask Questions About Your Documents")

    # Scope indicator
    if st.session_state.selected_doc:
        doc_meta = next(
            (d for d in st.session_state.documents if d["doc_id"] == st.session_state.selected_doc),
            None,
        )
        label = doc_meta["filename"] if doc_meta else st.session_state.selected_doc[:12]
        st.info(f"🔍 Searching in: **{label}**  _(change scope in sidebar)_")
    else:
        st.info("🔍 Searching across: **all documents**  _(select a specific doc in sidebar)_")

    # Render history
    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.markdown(
                f'<div class="answer-box">{turn["answer"]}</div>',
                unsafe_allow_html=True,
            )
            render_sources(turn.get("sources", []))

    # Input
    question = st.chat_input("Ask a question about your document(s)…")
    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer…"):
                result = api_post(
                    "/ask",
                    json_data={
                        "question": question,
                        "doc_id": st.session_state.selected_doc,
                        "top_k": 5,
                    },
                )

            if result:
                st.markdown(
                    f'<div class="answer-box">{result["answer"]}</div>',
                    unsafe_allow_html=True,
                )
                render_sources(result.get("sources", []))

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "sources": result.get("sources", []),
                })
            else:
                st.error("Failed to get an answer. Check that documents are uploaded and models are ready.")


# ──────────────────── SUMMARY TAB ───────────────────────────────────────────

with tab_summary:
    st.markdown("### Generate Document Summary")

    docs = st.session_state.documents
    if not docs:
        st.warning("No documents uploaded yet. Go to the Upload tab first.")
    else:
        selected_for_summary = st.selectbox(
            "Select document to summarize:",
            options=[(d["filename"], d["doc_id"]) for d in docs],
            format_func=lambda x: x[0],
        )

        if st.button("📋 Generate Summary", use_container_width=False):
            doc_name, doc_id = selected_for_summary
            with st.spinner(f"Summarizing '{doc_name}'… this may take a minute."):
                result = api_get(f"/summary/{doc_id}")

            if result:
                st.markdown(f"#### Summary: {doc_name}")

                meta_cols = st.columns(3)
                meta_cols[0].metric("Pages", result.get("total_pages") or "N/A")
                meta_cols[1].metric("Chunks analyzed", result["chunks_used"])
                meta_cols[2].metric("Doc ID", doc_id[:8] + "…")

                st.markdown("---")
                st.markdown(
                    f'<div class="card">{result["summary"]}</div>',
                    unsafe_allow_html=True,
                )

                # Download summary
                st.download_button(
                    label="⬇️ Download Summary",
                    data=result["summary"],
                    file_name=f"summary_{doc_name}.txt",
                    mime="text/plain",
                )


# ── Footer ─────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<div style="text-align:center; color:#555; font-size:0.8rem;">'
    "🔒 Secure Document Intelligence · Fully local · Powered by Phi-3 + nomic-embed-text + Qdrant"
    "</div>",
    unsafe_allow_html=True,
)
