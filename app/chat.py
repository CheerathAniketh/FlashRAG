from core.retriever import get_retriever
from core.llm import load_llm
from core.prompts import SYSTEM_PROMPT


def format_context(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def main():

    print("\n🔥 FlashRAG Chatbot Ready 🔥\n")

    retriever = get_retriever()
    llm = load_llm()

    while True:

        query = input("\nYou: ")

        if query.lower() in ["exit", "quit"]:
            print("Bye 👋")
            break

        # 1. Retrieve relevant chunks
        docs = retriever.invoke(query)

        # 2. Build context
        context = format_context(docs)

        # 3. Prompt
        prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{query}

Answer:
"""

        # 4. Get response
        response = llm.invoke(prompt)

        # 5. Output
        print("\nBot:", response.content)


if __name__ == "__main__":
    main()