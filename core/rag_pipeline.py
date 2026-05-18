"""
RAG Pipeline Orchestrator

This module wraps the existing chat logic and exposes a clean query interface
for use in the FastAPI application. It loads the retriever and LLM once on
initialization and reuses them for all queries.
"""

from typing import Tuple, List
from core.retriever import get_retriever
from core.llm import load_llm
from core.prompts import SYSTEM_PROMPT
from app.config import Config


class RAGPipeline:
    """
    Orchestration class for the RAG pipeline.
    
    Loads and caches the retriever and LLM on initialization.
    Provides a simple query interface for generating answers with sources.
    """
    
    def __init__(self) -> None:
        """
        Initialize the RAG pipeline by loading retriever and LLM.
        
        Raises:
            ValueError: If configuration validation fails
            FileNotFoundError: If ChromaDB not found
            RuntimeError: If component loading fails
        """
        # Validate configuration on startup
        Config.validate()
        
        # Load and cache retriever and LLM
        self.retriever = get_retriever()
        self.llm = load_llm()
    
    def _format_context(self, docs: List) -> str:
        """
        Format retrieved documents into readable context.
        
        Args:
            docs: List of Document objects from retriever
            
        Returns:
            str: Formatted context string
        """
        if not docs:
            return "[No relevant context found]"
        
        formatted = []
        for i, doc in enumerate(docs, 1):
            page = doc.metadata.get("page", "?")
            formatted.append(f"[Source: Page {page}]\n{doc.page_content}")
        
        return "\n\n---\n\n".join(formatted)
    
    def _extract_sources(self, docs: List) -> List[str]:
        """
        Extract source page information from retrieved documents.
        
        Args:
            docs: List of Document objects from retriever
            
        Returns:
            List[str]: List of source page strings
        """
        if not docs:
            return []
        
        sources = []
        for doc in docs:
            page = doc.metadata.get("page", "Unknown")
            source = f"Page {page}"
            if source not in sources:
                sources.append(source)
        
        return sources
    
    def query(self, question: str) -> Tuple[str, List[str]]:
        """
        Process a user question and generate an answer with sources.
        
        Args:
            question: User's question/query
            
        Returns:
            Tuple containing:
            - answer (str): Generated answer from LLM
            - sources (List[str]): List of source pages used
            
        Raises:
            ValueError: If question is empty
            RuntimeError: If LLM or retriever fails
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        try:
            # Retrieve relevant context
            docs = self.retriever.invoke(question)
            context = self._format_context(docs)
            sources = self._extract_sources(docs)
            
            # Build prompt with system message and context
            prompt = f"""{SYSTEM_PROMPT}

Context from documents:
{context}

Question:
{question}

Answer:"""
            
            # Generate response from LLM
            response = self.llm.invoke(prompt)
            answer = response.content
            
            return answer, sources
            
        except Exception as e:
            raise RuntimeError(f"Failed to process query: {str(e)}")
    
    def get_indexed_chunks_count(self) -> int:
        """
        Get the number of indexed chunks in the ChromaDB.
        
        Returns:
            int: Number of chunks/documents in the database
            
        Raises:
            RuntimeError: If unable to retrieve count
        """
        try:
            # Access the underlying Chroma collection to get document count
            if hasattr(self.retriever, '_vectorstore'):
                collection = self.retriever._vectorstore._collection
                return collection.count()
            
            # Fallback: try to count via the retriever's data
            # This is a best-effort approach
            return 0
            
        except Exception as e:
            raise RuntimeError(f"Failed to get indexed chunks count: {str(e)}")
