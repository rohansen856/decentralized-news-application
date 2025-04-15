"""
Health check routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, status
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor, get_mongodb, get_redis
from shared.models import HealthResponse
from shared.utils import health_check_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    try:
        services = {}
        
        def check_postgres():
            with get_postgres_cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        services.update(health_check_service('postgresql', check_postgres))
        
        def check_mongodb():
            db = get_mongodb()
            db.command('ping')
        
        services.update(health_check_service('mongodb', check_mongodb))
        
        def check_redis():
            redis_client = get_redis()
            redis_client.ping()
        
        services.update(health_check_service('redis', check_redis))
        
        all_healthy = all(status == "healthy" for status in services.values())
        status_code = "healthy" if all_healthy else "degraded"
        
        response = HealthResponse(
            status=status_code,
            services=services
        )
        
        if not all_healthy:
            raise HTTPException(status_code=503, detail=response.dict())
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail={'status': 'unhealthy', 'message': str(e)})


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        with get_postgres_cursor() as cursor:
            cursor.execute("SELECT 1")
        return {'status': 'ready'}
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        raise HTTPException(status_code=503, detail={'status': 'not ready', 'error': str(e)})


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {'status': 'alive'}