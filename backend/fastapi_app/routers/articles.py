"""
Article management routes for FastAPI backend
"""

import sys
import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import ArticleCreate, ArticleUpdate, ArticleResponse, PaginatedResponse
from shared.utils import (
    generate_uuid, calculate_reading_time, calculate_word_count,
    extract_keywords, calculate_quality_score, paginate_query_results, sanitize_html
)
from ..dependencies import get_current_user, get_optional_user

router = APIRouter()
logger = logging.getLogger(__name__)

def prepare_array_for_postgres(data):
    """
    Prepare array data for PostgreSQL insertion
    Handles both array columns (text[]) and JSON columns (jsonb)
    """
    if data is None:
        return []
    elif isinstance(data, list):
        # For PostgreSQL array columns, return the list as-is
        return data
    else:
        # Convert to list if it's not already
        return [str(data)]


def prepare_json_for_postgres(data):
    """
    Prepare JSON data for PostgreSQL insertion
    """
    from psycopg2.extras import Json
    if data is None:
        return Json({})
    elif isinstance(data, (dict, list)):
        return Json(data)
    else:
        return Json({"value": str(data)})


@router.get("/", response_model=PaginatedResponse)
async def get_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str = Query(""),
    language: str = Query(""),
    author_id: str = Query(""),
    status: str = Query("published"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc")
):
    """Get articles with filtering and pagination"""
    try:
        query = "SELECT * FROM articles WHERE status = %s"
        params = [status]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        if language:
            query += " AND language = %s"
            params.append(language)
        if author_id:
            query += " AND author_id = %s"
            params.append(author_id)
        
        valid_sort_fields = ['created_at', 'published_at', 'title', 'view_count', 'like_count', 'trending_score']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'desc'
        
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
        
        with get_postgres_cursor() as cursor:
            cursor.execute(query, params)
            articles = cursor.fetchall()
        
        article_responses = [ArticleResponse(**dict(article)) for article in articles]
        paginated = paginate_query_results([a.dict() for a in article_responses], page, per_page)
        
        return PaginatedResponse(**paginated)
    except Exception as e:
        logger.error(f"Get articles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve articles")


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    """Get article by ID and increment view count"""
    try:
        with get_postgres_cursor() as cursor:
            cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
            article_record = cursor.fetchone()
            
            if not article_record:
                raise HTTPException(status_code=404, detail="Article not found")
            
            cursor.execute("UPDATE articles SET view_count = view_count + 1 WHERE id = %s", (article_id,))
        
        return ArticleResponse(**dict(article_record))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get article error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve article")


@router.get("/{article_id}/related", response_model=List[ArticleResponse])
async def get_related_articles(article_id: str):
    """Get articles related to the given article by tags and category"""
    try:
        with get_postgres_cursor() as cursor:
            # First get the current article's tags and category
            cursor.execute("SELECT tags, category FROM articles WHERE id = %s", (article_id,))
            current_article = cursor.fetchone()
            
            if not current_article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            current_tags = current_article['tags'] or []
            current_category = current_article['category']
            
            # Find related articles by matching tags or category
            cursor.execute("""
                SELECT *, 
                CASE 
                    WHEN category = %s THEN 3
                    ELSE 0
                END +
                CASE 
                    WHEN tags && %s THEN array_length(tags & %s, 1) * 2
                    ELSE 0
                END as relevance_score
                FROM articles 
                WHERE id != %s 
                AND status = 'published'
                AND (category = %s OR tags && %s)
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT 6
            """, (
                current_category, current_tags, current_tags, article_id, 
                current_category, current_tags
            ))
            
            related_articles = cursor.fetchall()
            return [ArticleResponse(**dict(article)) for article in related_articles]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get related articles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve related articles")


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(article_data: ArticleCreate, current_user: dict = Depends(get_current_user)):
    """Create new article with proper array/JSON handling"""
    try:
        # Process article content
        sanitized_content = sanitize_html(article_data.content)
        reading_time = calculate_reading_time(sanitized_content)
        word_count = calculate_word_count(sanitized_content)
        seo_keywords = extract_keywords(sanitized_content)
        quality_score = calculate_quality_score(sanitized_content, article_data.title, article_data.summary)
        
        article_id = generate_uuid()
        author_id = current_user['id']
        
        tags_data = prepare_array_for_postgres(article_data.tags)  # For array columns
        metadata_data = prepare_json_for_postgres(article_data.metadata)  # For JSON columns
        seo_keywords_data = prepare_array_for_postgres(seo_keywords)  # For array columns
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                INSERT INTO articles (
                    id, title, content, summary, author_id, anonymous_author,
                    category, subcategory, tags, language, reading_time, word_count,
                    status, metadata, seo_keywords, quality_score, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                article_id, 
                article_data.title, 
                sanitized_content, 
                article_data.summary,
                author_id, 
                article_data.anonymous_author, 
                article_data.category,
                article_data.subcategory, 
                tags_data,  # Prepared for array column
                article_data.language,
                reading_time, 
                word_count, 
                'draft', 
                metadata_data,  # Prepared for JSON column
                seo_keywords_data,  # Prepared for array column
                quality_score, 
                datetime.now(),
                datetime.now()
            ))
            
            article_record = cursor.fetchone()
            
            if not article_record:
                raise HTTPException(status_code=500, detail="Failed to create article")
        
        logger.info(f"Article created successfully: {article_id} by user {author_id}")
        return ArticleResponse(**dict(article_record))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create article error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create article")