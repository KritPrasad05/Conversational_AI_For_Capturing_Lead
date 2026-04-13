import os
from langchain_community.vectorstores import FAISS
from rag.loader import load_knowledge_base
from rag.embedder import get_embedding_model

INDEX_PATH = "data/vector_store"


def create_vector_store():
    embeddings = get_embedding_model()

    if os.path.exists(os.path.join(INDEX_PATH, "index.faiss")):
        print("[RAG] Loading existing vector store...")
        try:
            vectorstore = FAISS.load_local(
                INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("[RAG] Vector store loaded successfully.")
            return vectorstore
        except Exception as e:
            print(f"[RAG] Failed to load saved index ({e}), rebuilding...")

    print("[RAG] Building vector store from knowledge base...")
    documents = load_knowledge_base()
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(INDEX_PATH)
    print("[RAG] Vector store built and saved.")
    return vectorstore