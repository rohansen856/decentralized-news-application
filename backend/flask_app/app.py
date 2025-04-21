"""
Flask Backend Application for Decentralized News Platform
Production-ready Flask API with comprehensive route handlers and proper CORS configuration
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import shared utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import db_manager
from shared.auth import auth_manager
from shared.models import *
from shared.utils import TimingContext, health_check_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('DEBUG', 'false').lower() == 'true'
    
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         expose_headers=['X-Response-Time'],
         supports_credentials=True,
         max_age=86400
    )
    
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'message': 'OK'})
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With,Accept")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
    # Import and register blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.articles import articles_bp
    from .routes.interactions import interactions_bp
    from .routes.recommendations import recommendations_bp
    from .routes.search import search_bp
    from .routes.analytics import analytics_bp
    from .routes.health import health_bp
    
    # Register blueprints with explicit trailing slash handling
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(articles_bp, url_prefix='/api/v1/articles')
    app.register_blueprint(interactions_bp, url_prefix='/api/v1/interactions')
    app.register_blueprint(recommendations_bp, url_prefix='/api/v1/recommendations')
    app.register_blueprint(search_bp, url_prefix='/api/v1/search')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(health_bp, url_prefix='/api/v1/health')
    
    # Disable automatic trailing slash redirects (common cause of preflight issues)
    app.url_map.strict_slashes = False
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        response = jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'error_code': 'NOT_FOUND'
        })
        # Ensure CORS headers on error responses
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        return response, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        response = jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        })
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        return response, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        response = jsonify({
            'success': False,
            'message': 'Bad request',
            'error_code': 'BAD_REQUEST'
        })
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        return response, 400
    
    # Request/Response middleware
    @app.before_request
    def before_request_logging():
        # Skip for OPTIONS requests to avoid interfering with preflight
        if request.method == 'OPTIONS':
            return
            
        request.start_time = datetime.now()
        
        # Log request
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = (datetime.now() - request.start_time).total_seconds() * 1000
            response.headers['X-Response-Time'] = f"{duration:.2f}ms"
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Ensure CORS headers are present
        origin = request.headers.get('Origin')
        if origin and origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    # Root endpoint to verify server is running
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Decentralized News Platform API',
            'version': '1.0.0',
            'status': 'running'
        })
    
    # API info endpoint
    @app.route('/api/v1')
    def api_info():
        return jsonify({
            'name': 'Decentralized News Platform API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'articles': '/api/v1/articles',
                'interactions': '/api/v1/interactions',
                'recommendations': '/api/v1/recommendations',
                'search': '/api/v1/search',
                'analytics': '/api/v1/analytics',
                'health': '/api/v1/health'
            }
        })
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # Development server configuration
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    logger.info(f"CORS origins: {os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=app.config['DEBUG'],
        threaded=True  # Enable threading for better concurrent request handling
    )