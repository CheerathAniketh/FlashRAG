from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import Config


def chunk_documents(documents):
    """
    Split documents into smaller chunks using recursive splitting.
    
    Args:
        documents: List of documents from loader
        
    Returns:
        List[Document]: Chunked documents with metadata
        
    Raises:
        ValueError: If no documents provided
    """
    
    if not documents:
        raise ValueError("❌ No documents to chunk")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]  # Smart splitting
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks
