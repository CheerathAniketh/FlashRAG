from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY

def load_llm():

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-8b-8192",
        temperature=0
    )

    return llm
