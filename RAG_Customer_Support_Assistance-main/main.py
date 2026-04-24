from modules.loader import load_pdf
from modules.chunker import chunk_documents
from modules.embedder import get_embedding_model
from modules.vector_store import create_vector_store, load_vector_store
from modules.retriever import get_retriever
from modules.generator import get_llm
from modules.graph import build_graph


# 🔹 STEP 1: Ingest PDF → Create Vector DB
def ingest():
    print("📄 Loading PDF...")
    docs = load_pdf("data/knowledge.pdf")

    print("✂️ Chunking documents...")
    chunks = chunk_documents(docs)

    print("🧠 Creating embeddings...")
    embedding_model = get_embedding_model()

    print("🗄️ Storing in ChromaDB...")
    create_vector_store(chunks, embedding_model)

    print("✅ Ingestion complete!\n")


# 🔹 STEP 2: Run Chatbot
def run_chat():
    print("🚀 Starting RAG Chatbot...")

    embedding_model = get_embedding_model()
    db = load_vector_store(embedding_model)
    retriever = get_retriever(db)
    llm = get_llm()

    app = build_graph(llm, retriever)

    print("\n🤖 RAG Customer Support Assistant Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting chatbot...")
            break

        result = app.invoke({"query": query})
        print("\nBot:", result["output"], "\n")


# 🔹 MAIN CONTROL
if __name__ == "__main__":
    print("Choose mode:")
    print("1. Ingest PDF")
    print("2. Run Chatbot")

    choice = input("Enter 1 or 2: ")

    if choice == "1":
        ingest()
    elif choice == "2":
        run_chat()
    else:
        print("❌ Invalid choice")