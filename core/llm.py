from langchain_groq import ChatGroq
from app.config import Config


def load_llm():
    """
    Load Groq LLM with error handling.
    
    Returns:
        ChatGroq: Initialized language model
        
    Raises:
        ValueError: If API key is missing
    """
    
    if not Config.GROQ_API_KEY:
        raise ValueError(
            "❌ GROQ_API_KEY not configured\n"
            "Add GROQ_API_KEY=your_key to .env file"
        )
    
    try:
        llm = ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            timeout=30  # Prevent hanging
        )
        print(f"LLM loaded: {Config.LLM_MODEL}")
        return llm
        
    except Exception as e:
        raise RuntimeError(f"❌ Failed to initialize Groq LLM: {str(e)}")