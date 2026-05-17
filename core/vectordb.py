from langchain_chroma import Chroma


def store_vectors(chunks, embeddings):
    """
    Store document chunks inside ChromaDB.
    """

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="data/chroma"
    )

    return vector_db