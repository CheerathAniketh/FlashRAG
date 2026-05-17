from langchain_chroma import Chroma

from core.embeddings import load_embedding_model

def get_retriever():
    """
    Load ChromaDB and create retriever.
    """

    embedding_model = load_embedding_model()

    vector_db = Chroma(
        persist_directory="data/chroma",
        embedding_function=embedding_model
    )

    retriever = vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    return retriever