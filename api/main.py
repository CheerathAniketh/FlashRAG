"""
FastAPI Main Application

Initializes the FastAPI application with CORS, middleware, and routes.
Implements MVP security by restricting CORS to specific domains.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.routes import router
from app.config import Config

# Create FastAPI application
app = FastAPI(
    title="FlashRAG API",
    description="REST API for Retrieval Augmented Generation (RAG) system with Data Structures in C knowledge base",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware (MVP Security)
# Only allow requests from specified domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.FRONTEND_DOMAINS,  # Restrict to frontend domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow GET and POST
    allow_headers=["Content-Type"],  # Only allow Content-Type header
)

# Include the API routes
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Returns welcome message and API info.
    
    Returns:
        dict: Welcome message and API documentation links
    """
    return {
        "message": "Welcome to FlashRAG API",
        "description": "Retrieval Augmented Generation system for Data Structures in C",
        "endpoints": {
            "chat": "POST /api/chat - Ask a question",
            "health": "GET /api/health - Check service health",
            "ingest": "POST /api/ingest - Upload PDF files",
            "docs": "GET /docs - Interactive API documentation (Swagger UI)",
            "redoc": "GET /redoc - Alternative API documentation (ReDoc)",
        }
    }


@app.get("/api", tags=["API Info"])
async def api_info():
    """
    API information endpoint - Returns available endpoints.
    
    Returns:
        dict: Information about available endpoints
    """
    return {
        "api_name": "FlashRAG API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat": "Process a user query and return an answer with sources",
            "GET /api/health": "Check service health and indexed chunks count",
            "POST /api/ingest": "Ingest PDF files into the knowledge base",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        }
    }


def custom_openapi():
    """
    Customize OpenAPI schema for better documentation.
    
    Returns:
        dict: Custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FlashRAG API",
        version="1.0.0",
        description="REST API for Retrieval Augmented Generation system",
        routes=app.routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "RAG",
            "description": "RAG system endpoints for chat and ingestion",
        },
        {
            "name": "Root",
            "description": "Root and informational endpoints",
        },
        {
            "name": "API Info",
            "description": "API information endpoints",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Returns welcome message and API info.
    
    Returns:
        dict: Welcome message and API documentation links
    """
    return {
        "message": "Welcome to FlashRAG API",
        "description": "Retrieval Augmented Generation system for Data Structures in C",
        "endpoints": {
            "chat": "POST /api/chat - Ask a question",
            "health": "GET /api/health - Check service health",
            "ingest": "POST /api/ingest - Upload PDF files",
            "docs": "GET /docs - Interactive API documentation (Swagger UI)",
            "redoc": "GET /redoc - Alternative API documentation (ReDoc)",
        }
    }


@app.get("/api", tags=["API Info"])
async def api_info():
    """
    API information endpoint - Returns available endpoints.
    
    Returns:
        dict: Information about available endpoints
    """
    return {
        "api_name": "FlashRAG API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat": "Process a user query and return an answer with sources",
            "GET /api/health": "Check service health and indexed chunks count",
            "POST /api/ingest": "Ingest PDF files into the knowledge base",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        }
    }


def custom_openapi():
    """
    Customize OpenAPI schema for better documentation.
    
    Returns:
        dict: Custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FlashRAG API",
        version="1.0.0",
        description="REST API for Retrieval Augmented Generation system",
        routes=app.routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "RAG",
            "description": "RAG system endpoints for chat and ingestion",
        },
        {
            "name": "Root",
            "description": "Root and informational endpoints",
        },
        {
            "name": "API Info",
            "description": "API information endpoints",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
