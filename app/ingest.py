from utils.loader import load_pdf
from utils.chunker import chunk_documents
from core.embeddings import load_embedding_model
from core.vectordb import store_vectors

docs = load_pdf("data/raw/DS Digital Notes - R25.pdf")

chunks = chunk_documents(docs)

embedding_model = load_embedding_model()

print(f"Loaded Pages: {len(docs)}")
print(f"Total Chunks: {len(chunks)}")

print(chunks[0].page_content)



vector_db = store_vectors(chunks, embedding_model)

print("Ingestion Complete")
print(f"Stored {len(chunks)} chunks in ChromaDB")


