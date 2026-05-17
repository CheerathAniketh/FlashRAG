from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY


def load_llm():

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    return llm

#model="llama-3.1-8b-instant" for debugging
