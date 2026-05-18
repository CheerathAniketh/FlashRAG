"""
Ingestion script: Load PDF → Chunk → Embed → Store in ChromaDB

Run this ONCE before using chat.py
"""

from app.config import Config
from utils.loader import load_pdf
from utils.chunker import chunk_documents
from core.embeddings import load_embedding_model
from core.vectordb import store_vectors


def ingest():
    """Run the full ingestion pipeline."""
    
    print("\n" + "="*50)
    print("📚 FlashRAG - Ingestion Pipeline")
    print("="*50 + "\n")
    
    try:
        # Validate config
        Config.validate()
        
        # Find PDF files
        pdf_files = list(Config.RAW_DIR.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {Config.RAW_DIR}")
            print("Add PDFs to data/raw/ and run again")
            return
        
        print(f"Found {len(pdf_files)} PDF(s)\n")
        
        all_chunks = []
        
        # Load and chunk each PDF
        for pdf_file in pdf_files:
            print(f"📖 Processing: {pdf_file.name}")
            docs = load_pdf(str(pdf_file))
            chunks = chunk_documents(docs)
            all_chunks.extend(chunks)
        
        # Load embedding model
        print("\n🔢 Loading embedding model...")
        embedding_model = load_embedding_model()
        
        # Store in ChromaDB
        print("\n💾 Storing in ChromaDB...")
        store_vectors(all_chunks, embedding_model)
        
        print("\n" + "="*50)
        print("✅ Ingestion Complete!")
        print("="*50)
        print(f"Total chunks: {len(all_chunks)}")
        print("\n➡️  Ready to use: python chat.py\n")
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}\n")
        return False
    
    return True


if __name__ == "__main__":
    ingest()