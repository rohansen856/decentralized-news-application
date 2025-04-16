"""
Health check routes for Flask backend
"""

from flask import Blueprint, jsonify
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor, get_mongodb, get_redis
from shared.models import HealthResponse
from shared.utils import health_check_service

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)


@health_bp.route('/', methods=['GET'])
def health_check():
    """Basic health check"""
    try:
        services = {}
        
        # PostgreSQL health check
        def check_postgres():
            with get_postgres_cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        services.update(health_check_service('postgresql', check_postgres))
        
        # MongoDB health check
        def check_mongodb():
            db = get_mongodb()
            db.command('ping')
        
        services.update(health_check_service('mongodb', check_mongodb))
        
        # Redis health check
        def check_redis():
            redis_client = get_redis()
            redis_client.ping()
        
        services.update(health_check_service('redis', check_redis))
        
        # Overall status
        all_healthy = all(status == "healthy" for status in services.values())
        status = "healthy" if all_healthy else "degraded"
        
        response = HealthResponse(
            status=status,
            services=services
        )
        
        return jsonify(response.dict()), 200 if all_healthy else 503
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 503


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Quick database connectivity check
        with get_postgres_cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return jsonify({'status': 'ready'}), 200
    
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        return jsonify({'status': 'not ready', 'error': str(e)}), 503


@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe"""
    return jsonify({'status': 'alive'}), 200