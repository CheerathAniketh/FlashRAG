import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List

# Load environment variables
load_dotenv()

# Configuration Class - Easy to extend for startup scale
class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Configs
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE = 0
    
    # Retrieval Configs
    RETRIEVAL_K = 3
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # API Request/Response Configs (MVP Production)
    MAX_QUERY_LENGTH = 500
    REQUEST_TIMEOUT = 35  # Seconds, longer than Groq timeout (30s)
    GROQ_RETRY_ATTEMPTS = 3
    
    # CORS Configuration for MVP
    FRONTEND_DOMAINS: List[str] = [
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "https://yourdomain.com",     # Production domain (update this)
    ]
    
    # Paths
    DATA_DIR = Path("data")
    RAW_DIR = DATA_DIR / "raw"
    CHROMA_DIR = DATA_DIR / "chroma"
    
    @classmethod
    def validate(cls):
        """Validate all critical configs on startup"""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "❌ GROQ_API_KEY not found in .env file\n"
                "Create .env file with: GROQ_API_KEY=your_key_here"
            )
        
        if not cls.RAW_DIR.exists():
            raise FileNotFoundError(
                f"❌ Data directory not found: {cls.RAW_DIR}\n"
                f"Create directory: mkdir -p {cls.RAW_DIR}"
            )
        
        print("✅ Configuration validated")
        return True

# For backward compatibility
GROQ_API_KEY = Config.GROQ_API_KEY