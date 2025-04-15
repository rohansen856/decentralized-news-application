"""
FastAPI Backend Application for Decentralized News Platform
Production-ready FastAPI application with comprehensive route handlers
"""

import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import db_manager
from shared.models import ErrorResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("FastAPI application starting up...")
    yield
    # Shutdown
    logger.info("FastAPI application shutting down...")
    db_manager.close_connections()


def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title="Decentralized News Platform API",
        description="FastAPI backend for decentralized news application with ML-powered recommendations",
        version="1.0.0",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan
    )
    
    # Security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    
    # CORS middleware
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = datetime.utcnow()
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
    
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
    
    # Import and include routers
    from .routers import auth, users, articles, interactions, recommendations, search, analytics, health
    
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(articles.router, prefix="/api/v1/articles", tags=["Articles"])
    app.include_router(interactions.router, prefix="/api/v1/interactions", tags=["Interactions"])
    app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
    
    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=exc.detail,
                error_code=f"HTTP_{exc.status_code}"
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error",
                error_code="INTERNAL_ERROR"
            ).dict()
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Decentralized News Platform FastAPI",
            "version": "1.0.0",
            "docs": "/api/v1/docs"
        }
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('FASTAPI_PORT', 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv('DEBUG', 'false').lower() == 'true',
        log_level="info"
    )