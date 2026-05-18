"""
API Request and Response Models

Pydantic models for request/response validation and documentation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import Config


class ChatRequest(BaseModel):
    """Request model for the /api/chat endpoint."""
    
    query: str = Field(..., min_length=1, max_length=Config.MAX_QUERY_LENGTH, description="User's question or query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are data structures in C?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for the /api/chat endpoint."""
    
    answer: str = Field(..., description="Generated answer from the LLM")
    sources: List[str] = Field(default_factory=list, description="List of source pages referenced")
    status: str = Field(default="success", description="Status of the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Data structures in C are ways of organizing and storing data...",
                "sources": ["Page 1", "Page 3"],
                "status": "success"
            }
        }


class HealthResponse(BaseModel):
    """Response model for the /api/health endpoint."""
    
    status: str = Field(..., description="Health status of the service")
    indexed_chunks: int = Field(..., description="Number of chunks indexed in ChromaDB")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "indexed_chunks": 284
            }
        }


class IngestResponse(BaseModel):
    """Response model for the /api/ingest endpoint."""
    
    status: str = Field(..., description="Status of the ingestion process")
    chunks_added: int = Field(..., description="Number of chunks added to the database")
    message: Optional[str] = Field(default=None, description="Additional message about the ingestion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "chunks_added": 50,
                "message": "Successfully ingested 1 PDF file with 50 chunks"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model for failed requests."""
    
    status: str = Field(default="error", description="Error status")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Invalid query provided",
                "detail": "Query cannot be empty"
            }
        }
