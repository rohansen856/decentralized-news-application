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


@router.get("/trending-topics")
async def get_trending_topics():
    """Get trending topics and tags"""
    try:
        with get_postgres_cursor() as cursor:
            # Get trending tags from recent articles
            cursor.execute("""
                SELECT 
                    tag, 
                    COUNT(*) as count,
                    ROUND((COUNT(*) * 100.0 / LAG(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) - 100), 1) as trend_percent
                FROM (
                    SELECT unnest(tags) as tag
                    FROM articles 
                    WHERE status = 'published' 
                    AND created_at >= %s
                ) tag_counts
                GROUP BY tag
                HAVING COUNT(*) >= 3
                ORDER BY count DESC
                LIMIT 10
            """, (datetime.now() - timedelta(days=7),))
            
            trending_topics = cursor.fetchall()
            
            # Format the response
            topics_list = []
            for topic in trending_topics:
                trend_percent = topic.get('trend_percent', 0) or 0
                topics_list.append({
                    "name": topic['tag'],
                    "count": topic['count'],
                    "trend": f"+{abs(trend_percent):.0f}%" if trend_percent >= 0 else f"{trend_percent:.0f}%"
                })
            
            return {"success": True, "topics": topics_list}
    
    except Exception as e:
        logger.error(f"Get trending topics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending topics")


@router.get("/reading-history")
async def get_reading_history(current_user: dict = Depends(get_current_user)):
    """Get user's reading history"""
    try:
        user_id = current_user['id']
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, MAX(ui.created_at) as last_interaction
                FROM articles a
                JOIN user_interactions ui ON a.id = ui.article_id
                WHERE ui.user_id = %s 
                AND ui.interaction_type IN ('view', 'like', 'save')
                AND a.status = 'published'
                GROUP BY a.id
                ORDER BY last_interaction DESC
                LIMIT 20
            """, (user_id,))
            
            articles = cursor.fetchall()
            article_responses = [ArticleResponse(**dict(article)) for article in articles]
            
            return {"success": True, "articles": article_responses}
    
    except Exception as e:
        logger.error(f"Get reading history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reading history")


@router.get("/user-stats")
async def get_user_recommendation_stats(current_user: dict = Depends(get_current_user)):
    """Get user reading statistics for recommendations"""
    try:
        user_id = current_user['id']
        
        with get_postgres_cursor() as cursor:
            # Get articles read count
            cursor.execute("""
                SELECT COUNT(DISTINCT article_id) as articles_read
                FROM user_interactions 
                WHERE user_id = %s AND interaction_type = 'view'
            """, (user_id,))
            articles_read = cursor.fetchone()['articles_read'] or 0
            
            # Get reading streak (consecutive days with reading activity)
            cursor.execute("""
                SELECT COUNT(*) as reading_streak
                FROM (
                    SELECT DISTINCT DATE(created_at) as reading_date
                    FROM user_interactions 
                    WHERE user_id = %s AND interaction_type = 'view'
                    AND created_at >= %s
                    ORDER BY reading_date DESC
                ) daily_reading
            """, (user_id, datetime.now() - timedelta(days=30)))
            reading_streak = cursor.fetchone()['reading_streak'] or 0
            
            # Get favorite topic (most interacted with tag)
            cursor.execute("""
                SELECT tag, COUNT(*) as interaction_count
                FROM (
                    SELECT unnest(a.tags) as tag
                    FROM articles a
                    JOIN user_interactions ui ON a.id = ui.article_id
                    WHERE ui.user_id = %s 
                    AND ui.interaction_type IN ('view', 'like', 'save')
                ) user_tags
                GROUP BY tag
                ORDER BY interaction_count DESC
                LIMIT 1
            """, (user_id,))
            favorite_topic_result = cursor.fetchone()
            favorite_topic = favorite_topic_result['tag'] if favorite_topic_result else 'General'
            
            return {
                "success": True,
                "stats": {
                    "articlesRead": articles_read,
                    "readingStreak": f"{reading_streak} days",
                    "favoriteTopic": favorite_topic
                }
            }
    
    except Exception as e:
        logger.error(f"Get user recommendation stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user stats")