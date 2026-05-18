"""
RAG Pipeline Orchestrator

This module wraps the existing chat logic and exposes a clean query interface
for use in the FastAPI application. It loads the retriever and LLM once on
initialization and reuses them for all queries.

Now with async support and Groq rate limit retry logic.
"""

import asyncio
from typing import Tuple, List
from core.retriever import get_retriever
from core.llm import load_llm
from core.prompts import SYSTEM_PROMPT
from core.rate_limiter import get_rate_limiter
from app.config import Config


class RAGPipeline:
    """
    Orchestration class for the RAG pipeline with async support.
    
    Loads and caches the retriever and LLM on initialization.
    Provides both sync and async query interfaces for generating answers with sources.
    Implements rate limit retry logic for Groq API calls.
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
        self.retriever, self.vector_db = get_retriever()
        self.llm = load_llm()
        
        # Initialize rate limiter for Groq retries
        self.rate_limiter = get_rate_limiter(max_attempts=Config.GROQ_RETRY_ATTEMPTS)
    
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
    
    async def _get_embeddings_async(self, question: str) -> List:
        """
        Asynchronously retrieve documents using embeddings (non-blocking).
        
        Runs the embedding lookup in a thread pool to avoid blocking the event loop.
        This allows handling many concurrent requests without performance degradation.
        
        Args:
            question: User's question/query
            
        Returns:
            List: Retrieved documents
            
        Raises:
            RuntimeError: If retrieval fails
        """
        try:
            # Run retriever in thread pool to avoid blocking
            docs = await asyncio.to_thread(self.retriever.invoke, question)
            return docs
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve documents: {str(e)}")
    
    async def _get_llm_response_async(self, prompt: str) -> str:
        """
        Asynchronously get LLM response with exponential backoff retry.
        
        Implements retry logic for Groq rate limits (429 errors).
        Retries with exponential backoff: 2s, 4s, 8s (up to 3 attempts).
        
        Args:
            prompt: Full prompt to send to LLM
            
        Returns:
            str: Generated answer from LLM
            
        Raises:
            RuntimeError: If all retry attempts fail or non-rate-limit error occurs
        """
        async def _invoke_llm() -> str:
            # Run LLM invocation in thread pool
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            return response.content
        
        # Use rate limiter to handle retries
        try:
            answer = await self.rate_limiter.retry_with_backoff(_invoke_llm)
            return answer
        except RuntimeError as e:
            # Re-raise rate limit errors with context
            if "rate limit" in str(e).lower():
                raise
            raise RuntimeError(f"LLM invocation failed: {str(e)}")
    
    async def query_async(self, question: str) -> Tuple[str, List[str]]:
        """
        Asynchronously process a user question and generate an answer with sources.
        
        Async version that doesn't block the event loop for embedding lookup or LLM calls.
        Implements exponential backoff retry for Groq rate limits.
        
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
            # Retrieve relevant context (non-blocking via thread pool)
            docs = await self._get_embeddings_async(question)
            context = self._format_context(docs)
            sources = self._extract_sources(docs)
            
            # Build prompt with system message and context
            prompt = f"""{SYSTEM_PROMPT}

Context from documents:
{context}

Question:
{question}

Answer:"""
            
            # Generate response from LLM (with retry logic)
            answer = await self._get_llm_response_async(prompt)
            
            return answer, sources
            
        except ValueError:
            # Re-raise validation errors
            raise
        except RuntimeError:
            # Re-raise runtime errors (including rate limit errors)
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to process query: {str(e)}")
    
    def query(self, question: str) -> Tuple[str, List[str]]:
        """
        Process a user question and generate an answer with sources (sync wrapper).
        
        Synchronous wrapper around query_async for backward compatibility.
        For async contexts, use query_async directly.
        
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
            
            # Generate response from LLM with retry logic
            answer = self.rate_limiter.retry_with_backoff_sync(self.llm.invoke, prompt).content
            
            return answer, sources
            
        except Exception as e:
            raise RuntimeError(f"Failed to process query: {str(e)}")
    
    def get_indexed_chunks_count(self) -> int:
        """
        Get the number of indexed chunks in ChromaDB using public API.
        
        Uses Chroma.get() method to retrieve all documents and count them.
        This properly queries the database instead of relying on private internals.
        
        Returns:
            int: Number of chunks/documents in the ChromaDB collection
            
        Raises:
            RuntimeError: If unable to retrieve count (but logs warning instead of raising)
        """
        try:
            # Use public Chroma API to get all documents
            # get() with no filters returns all documents in the collection
            results = self.vector_db.get()
            
            if results and 'ids' in results:
                count = len(results['ids'])
                return count
            
            # If no results, return 0
            return 0
            
        except Exception as e:
            # Log error but don't raise - return 0 for health check
            print(f"⚠️  Warning: Failed to get indexed chunks count: {str(e)}")
            return 0
