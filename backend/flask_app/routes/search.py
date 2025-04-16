"""
Search routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import SearchRequest, SearchResponse, ArticleResponse
from shared.utils import TimingContext

search_bp = Blueprint('search', __name__)
logger = logging.getLogger(__name__)


@search_bp.route('/', methods=['POST'])
def search_articles():
    """Search articles with full-text search"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            search_data = SearchRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False, 'message': 'Validation error', 'details': e.errors()
            }), 400
        
        with TimingContext() as timer:
            with get_postgres_cursor() as cursor:
                # Build search query
                query = """
                    SELECT *, ts_rank(
                        to_tsvector('english', title || ' ' || content || ' ' || summary), 
                        plainto_tsquery('english', %s)
                    ) as relevance_score
                    FROM articles 
                    WHERE status = 'published'
                """
                params = [search_data.query]
                
                # Add text search condition
                query += " AND (to_tsvector('english', title || ' ' || content || ' ' || summary) @@ plainto_tsquery('english', %s))"
                params.append(search_data.query)
                
                # Add filters
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
                
                # Pagination
                query += " LIMIT %s OFFSET %s"
                params.extend([search_data.limit, search_data.offset])
                
                cursor.execute(query, params)
                articles = cursor.fetchall()
                
                # Get total count
                count_query = """
                    SELECT COUNT(*) as total
                    FROM articles 
                    WHERE status = 'published'
                    AND (to_tsvector('english', title || ' ' || content || ' ' || summary) @@ plainto_tsquery('english', %s))
                """
                count_params = [search_data.query]
                
                if search_data.categories:
                    count_query += " AND category = ANY(%s)"
                    count_params.append(search_data.categories)
                
                if search_data.languages:
                    count_query += " AND language = ANY(%s)"
                    count_params.append(search_data.languages)
                
                if search_data.author_id:
                    count_query += " AND author_id = %s"
                    count_params.append(str(search_data.author_id))
                
                if search_data.date_from:
                    count_query += " AND published_at >= %s"
                    count_params.append(search_data.date_from)
                
                if search_data.date_to:
                    count_query += " AND published_at <= %s"
                    count_params.append(search_data.date_to)
                
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()['total']
        
        # Convert to response objects
        article_responses = [ArticleResponse(**dict(article)) for article in articles]
        
        response = SearchResponse(
            results=article_responses,
            total_count=total_count,
            query=search_data.query,
            execution_time_ms=timer.get_duration_ms()
        )
        
        return jsonify(response.dict()), 200
    
    except Exception as e:
        logger.error(f"Search articles error: {e}")
        return jsonify({
            'success': False,
            'message': 'Search failed'
        }), 500