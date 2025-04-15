"""
Search routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, status
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import SearchRequest, SearchResponse, ArticleResponse
from shared.utils import TimingContext

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SearchResponse)
async def search_articles(search_data: SearchRequest):
    """Search articles with full-text search"""
    try:
        with TimingContext() as timer:
            with get_postgres_cursor() as cursor:
                query = """
                    SELECT *, ts_rank(
                        to_tsvector('english', title || ' ' || content || ' ' || summary), 
                        plainto_tsquery('english', %s)
                    ) as relevance_score
                    FROM articles 
                    WHERE status = 'published'
                    AND (to_tsvector('english', title || ' ' || content || ' ' || summary) @@ plainto_tsquery('english', %s))
                """
                params = [search_data.query, search_data.query]
                
                if search_data.categories:
                    query += " AND category = ANY(%s)"
                    params.append(search_data.categories)
                
                if search_data.languages:
                    query += " AND language = ANY(%s)"
                    params.append(search_data.languages)
                
                if search_data.author_id:
                    query += " AND author_id = %s"
                    params.append(str(search_data.author_id))
                
                if search_data.date_from:
                    query += " AND published_at >= %s"
                    params.append(search_data.date_from)
                
                if search_data.date_to:
                    query += " AND published_at <= %s"
                    params.append(search_data.date_to)
                
                # Sorting
                if search_data.sort_by == 'relevance':
                    query += " ORDER BY relevance_score DESC"
                elif search_data.sort_by == 'date':
                    query += " ORDER BY published_at DESC"
                elif search_data.sort_by == 'popularity':
                    query += " ORDER BY engagement_score DESC"
                else:
                    query += " ORDER BY relevance_score DESC"
                
                query += " LIMIT %s OFFSET %s"
                params.extend([search_data.limit, search_data.offset])
                
                cursor.execute(query, params)
                articles = cursor.fetchall()
                
                # Get total count
                count_query = """
                    SELECT COUNT(*) as total FROM articles 
                    WHERE status = 'published'
                    AND (to_tsvector('english', title || ' ' || content || ' ' || summary) @@ plainto_tsquery('english', %s))
                """
                count_params = [search_data.query]
                
                if search_data.categories:
                    count_query += " AND category = ANY(%s)"
                    count_params.append(search_data.categories)
                
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()['total']
        
        article_responses = [ArticleResponse(**dict(article)) for article in articles]
        
        return SearchResponse(
            results=article_responses,
            total_count=total_count,
            query=search_data.query,
            execution_time_ms=timer.get_duration_ms()
        )
    
    except Exception as e:
        logger.error(f"Search articles error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")