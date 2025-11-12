import streamlit as st
from rag_pipeline import load_and_process_docs

st.set_page_config(page_title="📘 DocuMind – RAG Assistant", layout="wide")

st.title("📘 DocuMind – AI Document Assistant")
st.write("Upload PDFs and ask questions using Retrieval-Augmented Generation (RAG).")

uploaded_files = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    # Save uploaded files temporarily
    file_paths = []
    for f in uploaded_files:
        path = f"data/{f.name}"
        with open(path, "wb") as temp_file:
            temp_file.write(f.read())
        file_paths.append(path)

    st.info("🔄 Processing your documents… this may take a few seconds.")
    qa_chain = load_and_process_docs(file_paths)
    st.success("✅ Documents ready! Ask your questions below:")

    query = st.text_input("💭 Ask a question about your documents:")

    if query:
        result = qa_chain({"query": query})
        st.markdown("### 🧠 Answer:")
        st.write(result["result"])

        with st.expander("📚 Source References"):
            for doc in result["source_documents"]:
                st.write(doc.page_content[:300] + "...")
