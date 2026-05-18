from langchain_chroma import Chroma
from core.embeddings import load_embedding_model
from app.config import Config
from typing import Tuple


def get_retriever() -> Tuple:
    """
    Load ChromaDB and create retriever.
    
    Returns:
        Tuple containing:
        - retriever: LangChain retriever with k=3 similarity search
        - vector_db: Chroma vector database instance for direct access
        
    Raises:
        FileNotFoundError: If ChromaDB not found (run ingest.py first)
    """
    
    if not Config.CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"❌ ChromaDB not found at {Config.CHROMA_DIR}\n"
            "Run: python ingest.py (to index the PDF first)"
        )
    
    try:
        embedding_model = load_embedding_model()
        
        vector_db = Chroma(
            persist_directory=str(Config.CHROMA_DIR),
            embedding_function=embedding_model
        )
        
        retriever = vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": Config.RETRIEVAL_K}
        )
        
        print(f"✅ Retriever loaded (k={Config.RETRIEVAL_K})")
        return retriever, vector_db
        
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load ChromaDB: {str(e)}")