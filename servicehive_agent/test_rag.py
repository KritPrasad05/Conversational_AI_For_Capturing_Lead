from rag.vector_store import create_vector_store
from rag.retriever import get_retriever


def main():
    vectorstore = create_vector_store()
    retriever = get_retriever(vectorstore)

    query = "Do you support 4K videos?"

    docs = retriever.invoke(query)

    for doc in docs:
        print("\n--- Retrieved Chunk ---")
        print(doc.page_content)
        print("Metadata:", doc.metadata)


if __name__ == "__main__":
    main()