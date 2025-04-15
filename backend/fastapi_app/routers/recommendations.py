"""
Recommendations routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from datetime import datetime, timedelta
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor, get_redis
from shared.models import RecommendationRequest, RecommendationResponse, ArticleResponse
from shared.utils import cache_key_generator
from ..dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(req_data: RecommendationRequest, current_user: dict = Depends(get_current_user)):
    """Get personalized recommendations for user"""
    try:
        user_id = current_user['id']
        req_data.user_id = user_id
        
        # Check cache first
        cache_key = f"recommendations:{user_id}:{cache_key_generator(**req_data.dict())}"
        
        try:
            redis_client = get_redis()
            cached_result = redis_client.get(cache_key)
            if cached_result:
                cached_data = json.loads(cached_result)
                return RecommendationResponse(**cached_data)
        except Exception as redis_error:
            logger.warning(f"Redis cache error: {redis_error}")
        
        # Get recommendations from database
        with get_postgres_cursor() as cursor:
            # Check cached recommendations
            cursor.execute("""
                SELECT recommended_articles, recommendation_scores, model_ensemble, cache_timestamp, expiry_timestamp
                FROM recommendation_cache 
                WHERE user_id = %s AND is_active = true AND expiry_timestamp > %s
                ORDER BY cache_timestamp DESC LIMIT 1
            """, (user_id, datetime.now()))
            
            cached_rec = cursor.fetchone()
            
            if cached_rec:
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
                    
                    return response
            
            # Fallback: trending articles
            query = "SELECT * FROM articles WHERE status = 'published'"
            params = []
            
            if req_data.categories:
                query += " AND category = ANY(%s)"
                params.append(req_data.categories)
            
            if req_data.exclude_read:
                query += " AND id NOT IN (SELECT DISTINCT article_id FROM user_interactions WHERE user_id = %s AND interaction_type IN ('view', 'like', 'save'))"
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
            
            try:
                redis_client.setex(cache_key, 3600, json.dumps(response.model_dump(), default=str))
            except Exception as redis_error:
                logger.warning(f"Redis cache set error: {redis_error}")
            
            return response
    
    except Exception as e:
        logger.error(f"Get recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")