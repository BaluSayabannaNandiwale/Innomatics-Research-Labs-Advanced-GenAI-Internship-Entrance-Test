from langchain_community.vectorstores import Chroma

# 🔹 Create vector DB (used during ingestion)
def create_vector_store(chunks, embedding_model):
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="chroma_db"
    )
    
    # Persist data to disk
    db.persist()
    
    return db


# 🔹 Load existing vector DB (used during query/chat)
def load_vector_store(embedding_model):
    db = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_model
    )
    
    return db