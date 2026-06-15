"""
Secure Document Intelligence — Streamlit Frontend (Improved UI)
"""
import os
import time
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API = f"{BACKEND_URL}/api/v1"
TIMEOUT = 180

st.set_page_config(
    page_title="Secure Doc Intel",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Base ── */
    [data-testid="stSidebar"] { background: #0d0f18; border-right: 1px solid #1e2235; }
    .main { background: #0a0c14; }
    * { font-family: 'Inter', sans-serif; }

    /* ── Sidebar text ── */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown { color: #9aa3b8 !important; }

    /* ── Security badge ── */
    .sec-badge {
        background: linear-gradient(135deg, #0d2518, #0d1f2d);
        border: 1px solid #1a5c3a;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.78rem;
        color: #4caf7d;
        margin-bottom: 16px;
        letter-spacing: 0.3px;
    }

    /* ── Doc card in sidebar ── */
    .doc-card {
        background: #13172a;
        border: 1px solid #1e2748;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .doc-card:hover { border-color: #3d5afe; }
    .doc-card.active { border-color: #3d5afe; background: #161c38; }
    .doc-card-name { font-size: 0.85rem; color: #c8d0e8; font-weight: 500; }
    .doc-card-meta { font-size: 0.72rem; color: #5a6480; margin-top: 2px; }

    /* ── Answer box ── */
    .answer-wrap {
        background: #0f1322;
        border: 1px solid #1e2748;
        border-left: 4px solid #3d5afe;
        border-radius: 10px;
        padding: 18px 20px;
        font-size: 0.97rem;
        line-height: 1.75;
        color: #dde3f5;
        margin: 8px 0 16px 0;
    }

    /* ── Source card ── */
    .source-card {
        background: #0d1020;
        border: 1px solid #1a2040;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .source-label { font-size: 0.78rem; color: #7eb3ff; font-weight: 600; }
    .source-score { font-size: 0.72rem; color: #4caf7d; }
    .source-excerpt { font-size: 0.8rem; color: #6b7899; line-height: 1.5; }
    .score-bar-bg { background: #1a2040; border-radius: 4px; height: 3px; margin-top: 8px; }
    .score-bar-fill { height: 3px; border-radius: 4px;
        background: linear-gradient(90deg, #3d5afe, #00bcd4); }

    /* ── Upload drop zone ── */
    .upload-hint {
        text-align: center;
        color: #3a4060;
        font-size: 0.9rem;
        padding: 40px 20px;
        border: 2px dashed #1e2748;
        border-radius: 12px;
        margin-bottom: 16px;
    }

    /* ── Metric cards ── */
    .metric-row { display: flex; gap: 12px; margin: 16px 0; }
    .metric-card {
        flex: 1;
        background: #0d1020;
        border: 1px solid #1a2040;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .metric-val { font-size: 1.4rem; font-weight: 700; color: #7eb3ff; }
    .metric-lbl { font-size: 0.72rem; color: #5a6480; margin-top: 2px; }

    /* ── Status pill ── */
    .pill-ok  { display:inline-block; background:#0d2518; color:#4caf7d;
                border:1px solid #1a5c3a; border-radius:20px;
                padding:2px 10px; font-size:0.75rem; }
    .pill-err { display:inline-block; background:#2a0d0d; color:#ef5350;
                border:1px solid #5c1a1a; border-radius:20px;
                padding:2px 10px; font-size:0.75rem; }

    /* ── Chat input ── */
    [data-testid="stChatInput"] textarea {
        background: #0d1020 !important;
        border: 1px solid #1e2748 !important;
        color: #dde3f5 !important;
        border-radius: 10px !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #1e2748;
        color: #9aa3c8;
        border: 1px solid #2a3360;
        border-radius: 8px;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #3d5afe;
        color: white;
        border-color: #3d5afe;
    }

    /* ── Divider ── */
    hr { border-color: #1a1f35 !important; }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab"] { color: #5a6480; }
    .stTabs [aria-selected="true"] { color: #7eb3ff !important; }

    /* ── Toast-style success ── */
    .toast-ok {
        background: #0d2518; border: 1px solid #1a5c3a;
        border-radius: 8px; padding: 12px 16px;
        color: #4caf7d; font-size: 0.9rem; margin-bottom: 12px;
    }
    .toast-err {
        background: #2a0d0d; border: 1px solid #5c1a1a;
        border-radius: 8px; padding: 12px 16px;
        color: #ef5350; font-size: 0.9rem; margin-bottom: 12px;
    }

    /* hide streamlit default header */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend not reachable. Is the server running?")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def api_post(path, json_data=None, files=None):
    try:
        r = requests.post(f"{API}{path}", json=json_data, files=files, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend not reachable.")
        return None
    except requests.HTTPError as e:
        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
        st.error(f"Error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

def api_delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Delete error: {e}")
        return None

def render_sources(sources):
    if not sources:
        return
    st.markdown("**Referenced Sources**")
    for s in sources:
        score_pct = int(s.get("score", 0) * 100)
        bar_width = min(score_pct, 100)
        st.markdown(f"""
        <div class="source-card">
            <div class="source-header">
                <span class="source-label">📄 {s['source']} · Page {s['page']}</span>
                <span class="source-score">Relevance {score_pct}%</span>
            </div>
            <div class="source-excerpt">{s['excerpt']}</div>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{bar_width}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def refresh_docs():
    data = api_get("/documents")
    if data:
        st.session_state.documents = data["documents"]

# ── Session state ───────────────────────────────────────────────────────────
for key, val in {
    "selected_doc": None,
    "chat_history": [],
    "documents": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔒 Secure Doc Intel")
    st.markdown(
        '<div class="sec-badge">🛡️ 100% local &nbsp;·&nbsp; No cloud API &nbsp;·&nbsp; No data egress</div>',
        unsafe_allow_html=True
    )

    # Health
    if st.button("⚡ System Health", use_container_width=True):
        h = api_get("/health")
        if h:
            ok = h["status"] == "ok"
            st.markdown(
                f'<span class="{"pill-ok" if ok else "pill-err"}">{"✅ All systems OK" if ok else "⚠️ Degraded"}</span>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Qdrant:** {h['qdrant']}")
            st.markdown(f"**Ollama:** {h['ollama']}")
            st.markdown(f"**Model:** `{h['llm_model']}`")

    st.divider()

    # Documents
    st.markdown("**📁 Documents**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            refresh_docs()
    with col2:
        if st.button("➕ Upload", use_container_width=True):
            st.session_state["go_upload"] = True

    docs = st.session_state.documents
    if not docs:
        st.markdown(
            '<div style="color:#3a4060;font-size:0.8rem;padding:12px 0;">No documents yet.</div>',
            unsafe_allow_html=True
        )
    else:
        # All docs option
        all_selected = st.session_state.selected_doc is None
        if st.button(
            f"{'✅ ' if all_selected else ''}🌐 All documents",
            use_container_width=True
        ):
            st.session_state.selected_doc = None

        for d in docs:
            is_sel = st.session_state.selected_doc == d["doc_id"]
            label = f"{'✅ ' if is_sel else '📄 '}{d['filename'][:28]}"
            if st.button(label, use_container_width=True, key=f"doc_{d['doc_id']}"):
                st.session_state.selected_doc = d["doc_id"]

        # Delete selected
        if st.session_state.selected_doc:
            st.divider()
            if st.button("🗑️ Delete selected doc", use_container_width=True):
                res = api_delete(f"/documents/{st.session_state.selected_doc}")
                if res:
                    st.success("Deleted.")
                    st.session_state.selected_doc = None
                    st.session_state.documents = []
                    st.rerun()

    st.divider()
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ── Main ────────────────────────────────────────────────────────────────────
st.markdown("# 🔒 Secure Document Intelligence")
st.markdown(
    '<p style="color:#5a6480;margin-top:-8px;margin-bottom:20px;">'
    'Upload documents · Ask questions · Get cited answers — entirely offline</p>',
    unsafe_allow_html=True
)

tab_upload, tab_chat, tab_summary = st.tabs(["📤  Upload", "💬  Ask", "📋  Summary"])


# ── UPLOAD ──────────────────────────────────────────────────────────────────
with tab_upload:
    st.markdown("### Upload a Document")
    st.markdown(
        '<p style="color:#5a6480;font-size:0.88rem;">PDF, DOCX, or TXT · Max 50 MB · '
        'All processing is local — nothing leaves this machine.</p>',
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Drop your file here",
        type=["pdf", "docx", "doc", "txt"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.markdown(f"""
        <div style="background:#0d1020;border:1px solid #1a2040;border-radius:8px;
                    padding:14px 16px;margin-bottom:16px;">
            <div style="color:#c8d0e8;font-size:0.9rem;">📄 <b>{uploaded.name}</b></div>
            <div style="color:#5a6480;font-size:0.78rem;margin-top:4px;">
                {uploaded.size / 1024:.1f} KB · {uploaded.type or 'unknown type'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Ingest Document", type="primary"):
            with st.spinner("Extracting · Chunking · Embedding…"):
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                result = api_post("/upload", files=files)

            if result:
                st.markdown(f"""
                <div class="toast-ok">
                    ✅ <b>{result['filename']}</b> ingested successfully
                </div>
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-val">{result['chunks_stored']}</div>
                        <div class="metric-lbl">Chunks stored</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{result['pages']}</div>
                        <div class="metric-lbl">Pages</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{result['doc_id'][:6]}…</div>
                        <div class="metric-lbl">Doc ID</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                refresh_docs()
    else:
        st.markdown("""
        <div class="upload-hint">
            📂 Drag and drop a file above<br>
            <span style="font-size:0.8rem;color:#2a3360;">PDF · DOCX · TXT</span>
        </div>
        """, unsafe_allow_html=True)


# ── CHAT ────────────────────────────────────────────────────────────────────
with tab_chat:
    # Scope bar
    if st.session_state.selected_doc:
        doc_meta = next(
            (d for d in st.session_state.documents
             if d["doc_id"] == st.session_state.selected_doc), None
        )
        scope_name = doc_meta["filename"] if doc_meta else "Selected document"
        st.markdown(
            f'<div style="background:#0d1020;border:1px solid #1a2040;border-radius:8px;'
            f'padding:10px 14px;margin-bottom:16px;font-size:0.85rem;color:#7eb3ff;">'
            f'🔍 Searching in: <b>{scope_name}</b> '
            f'<span style="color:#3a4060;">· change in sidebar</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="background:#0d1020;border:1px solid #1a2040;border-radius:8px;'
            'padding:10px 14px;margin-bottom:16px;font-size:0.85rem;color:#5a6480;">'
            '🌐 Searching across <b style="color:#9aa3c8;">all documents</b></div>',
            unsafe_allow_html=True
        )

    if not st.session_state.documents:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#3a4060;">
            <div style="font-size:2.5rem;">📂</div>
            <div style="margin-top:12px;font-size:0.9rem;">Upload a document first to start asking questions</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render history
        for turn in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(turn["question"])
            with st.chat_message("assistant"):
                st.markdown(
                    f'<div class="answer-wrap">{turn["answer"]}</div>',
                    unsafe_allow_html=True
                )
                if turn.get("sources"):
                    render_sources(turn["sources"])
                if turn.get("elapsed"):
                    st.markdown(
                        f'<div style="color:#3a4060;font-size:0.72rem;'
                        f'text-align:right;margin-top:4px;">⏱ {turn["elapsed"]:.1f}s</div>',
                        unsafe_allow_html=True
                    )

        # Input
        question = st.chat_input("Ask a question about your document(s)…")
        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    t0 = time.time()
                    result = api_post("/ask", json_data={
                        "question": question,
                        "doc_id": st.session_state.selected_doc,
                        "top_k": 5,
                    })
                    elapsed = time.time() - t0

                if result:
                    answer = result["answer"]
                    sources = result.get("sources", [])

                    st.markdown(
                        f'<div class="answer-wrap">{answer}</div>',
                        unsafe_allow_html=True
                    )
                    render_sources(sources)
                    st.markdown(
                        f'<div style="color:#3a4060;font-size:0.72rem;'
                        f'text-align:right;margin-top:4px;">⏱ {elapsed:.1f}s</div>',
                        unsafe_allow_html=True
                    )

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": sources,
                        "elapsed": elapsed,
                    })
                else:
                    st.markdown(
                        '<div class="toast-err">❌ Could not get an answer. '
                        'Check backend logs.</div>',
                        unsafe_allow_html=True
                    )


# ── SUMMARY ─────────────────────────────────────────────────────────────────
with tab_summary:
    st.markdown("### Document Summary")

    docs = st.session_state.documents
    if not docs:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#3a4060;">
            <div style="font-size:2.5rem;">📋</div>
            <div style="margin-top:12px;font-size:0.9rem;">No documents uploaded yet</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        options = [(d["filename"], d["doc_id"]) for d in docs]
        chosen = st.selectbox(
            "Select document",
            options,
            format_func=lambda x: x[0],
            label_visibility="collapsed"
        )

        if st.button("📋 Generate Summary", type="primary"):
            name, doc_id = chosen
            with st.spinner(f"Summarizing '{name}'…"):
                t0 = time.time()
                result = api_get(f"/summary/{doc_id}")
                elapsed = time.time() - t0

            if result:
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-val">{result.get('total_pages') or '—'}</div>
                        <div class="metric-lbl">Pages</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{result['chunks_used']}</div>
                        <div class="metric-lbl">Chunks analysed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{elapsed:.1f}s</div>
                        <div class="metric-lbl">Time taken</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    f'<div class="answer-wrap">{result["summary"]}</div>',
                    unsafe_allow_html=True
                )

                st.download_button(
                    "⬇️ Download Summary",
                    data=result["summary"],
                    file_name=f"summary_{name}.txt",
                    mime="text/plain",
                )


# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<div style="text-align:center;color:#2a3060;font-size:0.75rem;padding:4px 0;">'
    '🔒 Secure Document Intelligence · Fully local · '
    'Phi-3 / Gemma · nomic-embed-text · Qdrant</div>',
    unsafe_allow_html=True
)