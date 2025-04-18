"""
Recommendations routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor, get_redis
from shared.auth import auth_required
from shared.models import RecommendationRequest, RecommendationResponse, ArticleResponse
from shared.utils import cache_key_generator

recommendations_bp = Blueprint('recommendations', __name__)
logger = logging.getLogger(__name__)


@recommendations_bp.route('/', methods=['POST'])
@auth_required
def get_recommendations():
    """Get personalized recommendations for user"""
    try:
        data = request.get_json() or {}
        user_id = request.current_user['id']
        data['user_id'] = user_id
        
        # Validate input
        try:
            req_data = RecommendationRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False, 'message': 'Validation error', 'details': e.errors()
            }), 400
        
        # Check cache first
        cache_key = f"recommendations:{user_id}:{cache_key_generator(**data)}"
        
        try:
            redis_client = get_redis()
            cached_result = redis_client.get(cache_key)
            if cached_result:
                cached_data = json.loads(cached_result)
                return jsonify(cached_data), 200
        except Exception as redis_error:
            logger.warning(f"Redis cache error: {redis_error}")
        
        # Get recommendations from database
        with get_postgres_cursor() as cursor:
            # First check if user has cached recommendations
            cursor.execute("""
                SELECT recommended_articles, recommendation_scores, model_ensemble, cache_timestamp, expiry_timestamp
                FROM recommendation_cache 
                WHERE user_id = %s AND is_active = true AND expiry_timestamp > %s
                ORDER BY cache_timestamp DESC LIMIT 1
            """, (user_id, datetime.now()))
            
            cached_rec = cursor.fetchone()
            
            if cached_rec:
                # Get article details
                article_ids = cached_rec['recommended_articles'][:req_data.limit]
                if article_ids:
                    cursor.execute("""
                        SELECT * FROM articles WHERE id = ANY(%s) AND status = 'published'
                        ORDER BY array_position(%s, id)
                    """, (article_ids, article_ids))
                    
                    articles = cursor.fetchall()
                    article_responses = [ArticleResponse(**dict(article)) for article in articles]
                    
                    response = RecommendationResponse(
                        recommendations=article_responses,
                        model_used=cached_rec['model_ensemble'],
                        generated_at=cached_rec['cache_timestamp'],
                        expires_at=cached_rec['expiry_timestamp']
                    )
                    
                    # Cache in Redis
                    try:
                        redis_client.setex(cache_key, 3600, json.dumps(response.dict(), default=str))
                    except Exception as redis_error:
                        logger.warning(f"Redis cache set error: {redis_error}")
                    
                    return jsonify(response.dict()), 200
            
            # Fallback: Get popular articles
            query = """
                SELECT * FROM articles 
                WHERE status = 'published'
            """
            params = []
            
            if req_data.categories:
                query += " AND category = ANY(%s)"
                params.append(req_data.categories)
            
            if req_data.exclude_read:
                query += """ 
                    AND id NOT IN (
                        SELECT DISTINCT article_id FROM user_interactions 
                        WHERE user_id = %s AND interaction_type IN ('view', 'like', 'save')
                    )
                """
                params.append(user_id)
            
            query += " ORDER BY trending_score DESC, engagement_score DESC LIMIT %s"
            params.append(req_data.limit)
            
            cursor.execute(query, params)
            articles = cursor.fetchall()
            
            article_responses = [ArticleResponse(**dict(article)) for article in articles]
            
            response = RecommendationResponse(
                recommendations=article_responses,
                model_used="trending_fallback",
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
            # Cache in Redis
            try:
                redis_client.setex(cache_key, 3600, json.dumps(response.dict(), default=str))
            except Exception as redis_error:
                logger.warning(f"Redis cache set error: {redis_error}")
            
            return jsonify(response.dict()), 200
    
    except Exception as e:
        logger.error(f"Get recommendations error: {e}")
        return jsonify({'success': False, 'message': 'Failed to get recommendations'}), 500