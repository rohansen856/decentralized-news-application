"""
Article management routes for FastAPI backend
"""

import sys
import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
import logging

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


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(article_data: ArticleCreate, current_user: dict = Depends(get_current_user)):
    """Create new article"""
    try:
        sanitized_content = sanitize_html(article_data.content)
        reading_time = calculate_reading_time(sanitized_content)
        word_count = calculate_word_count(sanitized_content)
        seo_keywords = extract_keywords(sanitized_content)
        quality_score = calculate_quality_score(sanitized_content, article_data.title, article_data.summary)
        
        article_id = generate_uuid()
        author_id = current_user['id']
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                INSERT INTO articles (
                    id, title, content, summary, author_id, anonymous_author,
                    category, subcategory, tags, language, reading_time, word_count,
                    status, metadata, seo_keywords, quality_score, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                article_id, article_data.title, sanitized_content, article_data.summary,
                author_id, article_data.anonymous_author, article_data.category,
                article_data.subcategory, article_data.tags, article_data.language,
                reading_time, word_count, 'draft', article_data.metadata or {},
                seo_keywords, quality_score, 'now()', 'now()'
            ))
            
            article_record = cursor.fetchone()
        
        return ArticleResponse(**dict(article_record))
    except Exception as e:
        logger.error(f"Create article error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create article")