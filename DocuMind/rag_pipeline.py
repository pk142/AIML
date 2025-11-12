import os
from fpdf import FPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

DATA_DIR = "data"
SAMPLE_FILE = os.path.join(DATA_DIR, "sample.pdf")

def ensure_sample_pdf():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(SAMPLE_FILE):
        print("📄 Creating sample.pdf...")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        text = """Company Policy Overview

1. Working Hours: Employees work 8 hours/day, 9 AM–6 PM, Mon–Fri.
2. Leave Policy:
   - Casual : 10 days
   - Sick : 7 days
   - Maternity : 6 months
   - Paternity : 15 days
3. Work From Home allowed with manager approval.
4. Code of Conduct requires professionalism and confidentiality.
"""
        pdf.multi_cell(0, 10, text)
        pdf.output(SAMPLE_FILE)
        print(f"✅ Created sample PDF at {SAMPLE_FILE}")
    else:
        print(f"✅ Found existing PDF at {SAMPLE_FILE}")

def load_and_process_docs(file_paths):
    ensure_sample_pdf()

    docs = []
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ File not found: {path}")
        loader = PyPDFLoader(path)
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model="llama3")
    vectordb = Chroma.from_documents(chunks, embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = ChatOllama(model="llama3")

    prompt = ChatPromptTemplate.from_template(
        "Answer the question using the context below.\n\n{context}\n\nQuestion: {question}"
    )

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain
