"""
API Routes and Endpoints

Defines the REST API endpoints for the RAG system with async support,
input validation, and enhanced error handling.
"""

import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from typing import List
import os
from pathlib import Path

from api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    IngestResponse,
    ErrorResponse,
)
from core.rag_pipeline import RAGPipeline
from app.config import Config
from utils.loader import load_pdf
from utils.chunker import chunk_documents
from core.embeddings import load_embedding_model
from core.vectordb import store_vectors

# Create router
router = APIRouter(prefix="/api", tags=["RAG"])

# Global RAG pipeline instance (initialized once)
_rag_pipeline: RAGPipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or initialize the global RAG pipeline instance.
    
    This ensures the pipeline is only initialized once and reused
    for all requests, avoiding redundant loading of models.
    
    Returns:
        RAGPipeline: The initialized RAG pipeline
        
    Raises:
        RuntimeError: If pipeline initialization fails
    """
    global _rag_pipeline
    
    if _rag_pipeline is None:
        try:
            _rag_pipeline = RAGPipeline()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize RAG pipeline: {str(e)}")
    
    return _rag_pipeline


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint - Process a user query and return an answer with sources.
    
    Includes:
    - Input validation (max 500 chars, min 1 char)
    - Request timeout (35s, longer than Groq timeout)
    - Exponential backoff retry for Groq rate limits
    - User-friendly error messages
    
    Args:
        request: ChatRequest containing the user's query
        
    Returns:
        ChatResponse: Generated answer, sources, and status
        
    Raises:
        HTTPException: If query processing fails with appropriate status codes
    """
    try:
        # Validate query length
        if len(request.query) > Config.MAX_QUERY_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question too long. Maximum {Config.MAX_QUERY_LENGTH} characters allowed."
            )
        
        if len(request.query) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty."
            )
        
        # Get the RAG pipeline
        pipeline = get_rag_pipeline()
        
        # Process the query with timeout
        try:
            answer, sources = await asyncio.wait_for(
                pipeline.query_async(request.query),
                timeout=Config.REQUEST_TIMEOUT
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request took too long to process. Please try again."
            )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            status="success"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Invalid input (from validation)
        error_msg = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg if error_msg else "Invalid question provided."
        )
    except RuntimeError as e:
        # Processing error - distinguish between rate limit and other errors
        error_msg = str(e)
        
        if "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Server is busy. Please try again in a few minutes."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process your question. Please try again."
            )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health() -> HealthResponse:
    """
    Health check endpoint - Returns service status and indexed chunks count.
    
    Returns:
        HealthResponse: Service status and number of indexed chunks
        
    Raises:
        HTTPException: If health check fails
    """
    try:
        # Get the RAG pipeline to ensure all components are loaded
        pipeline = get_rag_pipeline()
        
        # Try to get indexed chunks count
        try:
            indexed_chunks = pipeline.get_indexed_chunks_count()
        except Exception:
            # If we can't get the count, return 0
            indexed_chunks = 0
        
        return HealthResponse(
            status="healthy",
            indexed_chunks=indexed_chunks
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready. Please try again later."
        )


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest(files: List[UploadFile] = File(...)) -> IngestResponse:
    """
    Ingest endpoint - Upload and process PDF files.
    
    Args:
        files: List of PDF files to ingest
        
    Returns:
        IngestResponse: Status and number of chunks added
        
    Raises:
        HTTPException: If ingestion fails
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided."
        )
    
    try:
        # Validate configuration
        Config.validate()
        
        # Ensure raw data directory exists
        Config.RAW_DIR.mkdir(parents=True, exist_ok=True)
        
        total_chunks = 0
        processed_files = 0
        
        # Process each uploaded file
        for file in files:
            # Validate file type
            if not file.filename or not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type: {file.filename}. Only PDF files are accepted."
                )
            
            try:
                # Save uploaded file temporarily
                temp_path = Config.RAW_DIR / file.filename
                
                # Read and save the file
                content = await file.read()
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                # Load and process the PDF
                docs = load_pdf(str(temp_path))
                chunks = chunk_documents(docs)
                
                # Load embedding model and store vectors
                embedding_model = load_embedding_model()
                store_vectors(chunks, embedding_model)
                
                total_chunks += len(chunks)
                processed_files += 1
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to process file {file.filename}. Please try again."
                )
        
        return IngestResponse(
            status="success",
            chunks_added=total_chunks,
            message=f"Successfully ingested {processed_files} PDF file(s) with {total_chunks} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ingestion failed. Please try again."
        )
