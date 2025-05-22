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
from starlette.exceptions import HTTPException as StarletteHTTPException
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
    
    # Test database connections on startup
    try:
        from shared.database import test_all_connections
        connection_results = test_all_connections()
        logger.info(f"Database connection test results: {connection_results}")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("FastAPI application shutting down...")
    try:
        db_manager.close_connections()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


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
    
    # Custom middleware with proper error handling
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        try:
            start_time = datetime.now()
            response = await call_next(request)
            process_time = (datetime.now() - start_time).total_seconds() * 1000
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            return response
        except Exception as e:
            logger.error(f"Process time middleware error: {e}")
            # Create a fallback response
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Request processing failed",
                    "error_code": "MIDDLEWARE_ERROR",
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        try:
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            return response
        except Exception as e:
            logger.error(f"Security headers middleware error: {e}")
            # If security headers fail, still try to return the response
            return await call_next(request)
    
    # Import and include routers
    try:
        from .routers import auth, users, articles, interactions, recommendations, search, analytics, health, donations
        
        app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
        app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
        app.include_router(articles.router, prefix="/api/v1/articles", tags=["Articles"])
        app.include_router(interactions.router, prefix="/api/v1/interactions", tags=["Interactions"])
        app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
        app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
        app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
        app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
        app.include_router(donations.router, prefix="/api/v1/donations", tags=["Donations"])
        
        logger.info("All routers included successfully")
    except ImportError as e:
        logger.error(f"Failed to import routers: {e}")
        # You might want to include only the routers that exist
        try:
            from .routers import auth
            app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
            logger.info("Auth router included successfully")
        except ImportError:
            logger.error("Failed to import auth router")
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions - bypass ErrorResponse model"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": f"HTTP_{exc.status_code}",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(HTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions - bypass ErrorResponse model"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": f"HTTP_{exc.status_code}",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions - bypass ErrorResponse model"""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Decentralized News Platform FastAPI",
            "version": "1.0.0",
            "docs": "/api/v1/docs",
            "health": "/api/v1/health",
            "timestamp": datetime.now().isoformat()
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Simple health check endpoint"""
        try:
            # Test database connection
            from shared.database import test_all_connections
            db_status = test_all_connections()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": db_status,
                "version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
            )
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('FASTAPI_PORT', 8000))
    host = os.getenv('FASTAPI_HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting FastAPI server on {host}:{port} (debug={debug})")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
        access_log=True
    )