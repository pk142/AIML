from rag_pipeline import load_and_process_docs, SAMPLE_FILE

qa_chain = load_and_process_docs([SAMPLE_FILE])

# 👇 replace with an actual PDF path in your data folder
#file_paths = ["data/sample.pdf"]

#qa_chain = load_and_process_docs(file_paths)

query = "Summarize the main topic of this document."
result = qa_chain.invoke({"input": query})

print("\n🧠 Answer:")
print(result["answer"])
