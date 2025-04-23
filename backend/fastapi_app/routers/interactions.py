"""
User interactions routes for FastAPI backend
"""

import sys
import os
import json
from fastapi import APIRouter, HTTPException, Depends, status
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import InteractionCreate, InteractionResponse
from shared.utils import generate_uuid, generate_session_id
from ..dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(interaction_data: InteractionCreate, current_user: dict = Depends(get_current_user)):
    """Record user interaction with article"""
    try:
        user_id = current_user['id']
        interaction_id = generate_uuid()
        session_id = generate_session_id(user_id)
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_interactions (
                    id, user_id, article_id, interaction_type, interaction_strength,
                    reading_progress, time_spent, device_type, context_data, session_id, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
            """, (
                interaction_id, user_id, str(interaction_data.article_id),
                interaction_data.interaction_type.value, interaction_data.interaction_strength,
                interaction_data.reading_progress, interaction_data.time_spent,
                interaction_data.device_type, json.dumps(interaction_data.context_data or {}),
                session_id, 'now()'
            ))
            
            interaction_record = cursor.fetchone()
        
        return InteractionResponse(**dict(interaction_record))
    except Exception as e:
        logger.error(f"Create interaction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.post("/{article_id}/like")
async def like_article(article_id: str, current_user: dict = Depends(get_current_user)):
    """Like/unlike an article"""
    try:
        user_id = current_user['id']
        
        with get_postgres_cursor() as cursor:
            # Check if user already liked this article
            cursor.execute("""
                SELECT id FROM user_interactions 
                WHERE user_id = %s AND article_id = %s AND interaction_type = 'like'
            """, (user_id, article_id))
            
            existing_like = cursor.fetchone()
            
            if existing_like:
                # Remove like
                cursor.execute("""
                    DELETE FROM user_interactions 
                    WHERE user_id = %s AND article_id = %s AND interaction_type = 'like'
                """, (user_id, article_id))
                
                # Update article like count
                cursor.execute("""
                    UPDATE articles SET like_count = like_count - 1 
                    WHERE id = %s AND like_count > 0
                """, (article_id,))
                
                return {"success": True, "liked": False, "message": "Article unliked"}
            else:
                # Add like
                interaction_id = generate_uuid()
                session_id = generate_session_id(user_id)
                
                cursor.execute("""
                    INSERT INTO user_interactions (
                        id, user_id, article_id, interaction_type, interaction_strength,
                        context_data, session_id, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    interaction_id, user_id, article_id, 'like', 1.0,
                    json.dumps({}), session_id, 'now()'
                ))
                
                # Update article like count
                cursor.execute("""
                    UPDATE articles SET like_count = like_count + 1 
                    WHERE id = %s
                """, (article_id,))
                
                return {"success": True, "liked": True, "message": "Article liked"}
                
    except Exception as e:
        logger.error(f"Like article error: {e}")
        raise HTTPException(status_code=500, detail="Failed to like article")


@router.post("/{article_id}/bookmark")
async def bookmark_article(article_id: str, current_user: dict = Depends(get_current_user)):
    """Bookmark/unbookmark an article"""
    try:
        user_id = current_user['id']
        
        with get_postgres_cursor() as cursor:
            # Check if user already bookmarked this article
            cursor.execute("""
                SELECT id FROM saved_articles 
                WHERE user_id = %s AND article_id = %s
            """, (user_id, article_id))
            
            existing_bookmark = cursor.fetchone()
            
            if existing_bookmark:
                # Remove bookmark
                cursor.execute("""
                    DELETE FROM saved_articles 
                    WHERE user_id = %s AND article_id = %s
                """, (user_id, article_id))
                
                return {"success": True, "bookmarked": False, "message": "Article unbookmarked"}
            else:
                # Add bookmark
                bookmark_id = generate_uuid()
                
                cursor.execute("""
                    INSERT INTO saved_articles (
                        id, user_id, article_id, collection_name, created_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    bookmark_id, user_id, article_id, 'default', 'now()'
                ))
                
                # Record interaction
                interaction_id = generate_uuid()
                session_id = generate_session_id(user_id)
                
                cursor.execute("""
                    INSERT INTO user_interactions (
                        id, user_id, article_id, interaction_type, interaction_strength,
                        context_data, session_id, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    interaction_id, user_id, article_id, 'save', 1.0,
                    json.dumps({}), session_id, 'now()'
                ))
                
                return {"success": True, "bookmarked": True, "message": "Article bookmarked"}
                
    except Exception as e:
        logger.error(f"Bookmark article error: {e}")
        raise HTTPException(status_code=500, detail="Failed to bookmark article")


@router.post("/{article_id}/share")
async def share_article(article_id: str, share_data: dict, current_user: dict = Depends(get_current_user)):
    """Record article share"""
    try:
        user_id = current_user['id']
        platform = share_data.get('platform', 'unknown')
        interaction_id = generate_uuid()
        session_id = generate_session_id(user_id)
        
        with get_postgres_cursor() as cursor:
            # Record share interaction
            cursor.execute("""
                INSERT INTO user_interactions (
                    id, user_id, article_id, interaction_type, interaction_strength,
                    context_data, session_id, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                interaction_id, user_id, article_id, 'share', 1.0,
                json.dumps({"platform": platform}), session_id, 'now()'
            ))
            
            # Update article share count
            cursor.execute("""
                UPDATE articles SET share_count = share_count + 1 
                WHERE id = %s
            """, (article_id,))
            
            return {"success": True, "message": f"Article shared to {platform}"}
                
    except Exception as e:
        logger.error(f"Share article error: {e}")
        raise HTTPException(status_code=500, detail="Failed to share article")


@router.get("/{article_id}/status")
async def get_article_interaction_status(article_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's interaction status with article"""
    try:
        user_id = current_user['id']
        logger.info(f"Getting interaction status for article {article_id} and user {user_id}")
        
        with get_postgres_cursor() as cursor:
            # First check if article exists
            cursor.execute("SELECT id FROM articles WHERE id = %s", (article_id,))
            article_exists = cursor.fetchone()
            
            if not article_exists:
                logger.warning(f"Article {article_id} not found")
                raise HTTPException(status_code=404, detail="Article not found")
            
            # Check if user liked the article
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM user_interactions 
                    WHERE user_id = %s AND article_id = %s AND interaction_type = 'like'
                )
            """, (user_id, article_id))
            liked_result = cursor.fetchone()
            liked = liked_result['exists'] if liked_result else False
            
            # Check if user bookmarked the article
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM saved_articles 
                    WHERE user_id = %s AND article_id = %s
                )
            """, (user_id, article_id))
            bookmarked_result = cursor.fetchone()
            bookmarked = bookmarked_result['exists'] if bookmarked_result else False
            
            # Get article stats
            cursor.execute("""
                SELECT like_count, view_count, share_count, comment_count
                FROM articles WHERE id = %s
            """, (article_id,))
            stats = cursor.fetchone()
            
            if not stats:
                logger.warning(f"No stats found for article {article_id}")
                stats_dict = {"likes": 0, "views": 0, "shares": 0, "comments": 0}
            else:
                stats_dict = {
                    "likes": stats['like_count'] or 0,
                    "views": stats['view_count'] or 0,
                    "shares": stats['share_count'] or 0,
                    "comments": stats['comment_count'] or 0
                }
            
            return {
                "success": True,
                "liked": liked,
                "bookmarked": bookmarked,
                "stats": stats_dict
            }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get interaction status error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get interaction status")