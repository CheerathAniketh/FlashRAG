from langchain_chroma import Chroma
from app.config import Config


def store_vectors(chunks, embeddings):
    """
    Store document chunks in ChromaDB.
    
    Args:
        chunks: List of document chunks from chunker
        embeddings: Embedding model from load_embedding_model()
        
    Returns:
        Chroma: Persisted vector database
        
    Raises:
        RuntimeError: If storage fails
    """
    
    if not chunks:
        raise ValueError("❌ No chunks to store")
    
    try:
        # Ensure persist directory exists
        Config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(Config.CHROMA_DIR)
        )
        
        print(f"✅ Stored {len(chunks)} chunks in ChromaDB")
        return vector_db
        
    except Exception as e:
        raise RuntimeError(f"❌ Failed to store vectors: {str(e)}")