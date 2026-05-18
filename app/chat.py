print('Started Chat')
from core.retriever import get_retriever
from core.llm import load_llm
from core.prompts import SYSTEM_PROMPT
from app.config import Config
print('Imports DONE')

def format_context(docs):
    """Format retrieved documents into readable context."""
    if not docs:
        return "[No relevant context found]"
    
    formatted = []
    for i, doc in enumerate(docs, 1):
        page = doc.metadata.get("page", "?")
        formatted.append(f"[Source: Page {page}]\n{doc.page_content}")
    
    return "\n\n---\n\n".join(formatted)


def main():
    """Main chat loop with error handling."""
    
    print("\n" + "="*50)
    print("🔥 FlashRAG - RAG Chatbot 🔥")
    print("="*50)
    print("Type 'exit' or 'quit' to stop\n")
    
    try:
        # Validate config on startup
        Config.validate()
        
        # Load components
        print("\n📚 Loading retriever...")
        retriever = get_retriever()
        
        print("🤖 Loading LLM...")
        llm = load_llm()
        
        print("\n✅ Ready for questions!\n")
        
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"\n{e}")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error during startup: {e}")
        return
    
    # Chat loop
    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            # Exit conditions
            if not query:
                continue
            
            if query.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye!")
                break
            
            # Retrieve context
            docs = retriever.invoke(query)
            context = format_context(docs)
            
            # Build prompt
            prompt = f"""{SYSTEM_PROMPT}

Context from documents:
{context}

Question:
{query}

Answer:"""
            
            # Get response
            print("\n🤖 Bot: ", end="", flush=True)
            response = llm.invoke(prompt)
            print(response.content)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("(Continuing...)\n")


if __name__ == "__main__":
    main()