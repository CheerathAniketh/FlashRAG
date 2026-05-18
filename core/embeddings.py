from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config


def load_embedding_model():
    """
    Load Hugging Face embedding model.
    
    Returns:
        HuggingFaceEmbeddings: Embedding model
        
    Raises:
        RuntimeError: If model fails to load
    """
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )
        print(f"Embeddings loaded: {Config.EMBEDDING_MODEL}")
        return embeddings
        
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load embeddings: {str(e)}")