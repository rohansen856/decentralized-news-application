"""
Article management routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.auth import auth_required
from shared.models import ArticleCreate, ArticleUpdate, ArticleResponse
from shared.utils import (
    generate_uuid, calculate_reading_time, calculate_word_count,
    extract_keywords, calculate_quality_score, paginate_query_results,
    sanitize_html
)

articles_bp = Blueprint('articles', __name__)
logger = logging.getLogger(__name__)


@articles_bp.route('/', methods=['GET'])
def get_articles():
    """Get list of articles with filtering and pagination"""
    try:
        # Pagination parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Filter parameters
        category = request.args.get('category', '')
        language = request.args.get('language', '')
        author_id = request.args.get('author_id', '')
        status = request.args.get('status', 'published')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
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
        
        # Sorting
        valid_sort_fields = ['created_at', 'published_at', 'title', 'view_count', 'like_count', 'trending_score']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'desc'
        
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
        
        with get_postgres_cursor() as cursor:
            cursor.execute(query, params)
            articles = cursor.fetchall()
        
        # Convert to response objects
        article_responses = [ArticleResponse(**dict(article)) for article in articles]
        
        # Paginate results
        paginated = paginate_query_results([a.dict() for a in article_responses], page, per_page)
        
        return jsonify({
            'success': True,
            **paginated
        }), 200
    
    except Exception as e:
        logger.error(f"Get articles error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve articles'
        }), 500


@articles_bp.route('/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get article by ID"""
    try:
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM articles WHERE id = %s",
                (article_id,)
            )
            
            article_record = cursor.fetchone()
            if not article_record:
                return jsonify({
                    'success': False,
                    'message': 'Article not found'
                }), 404
            
            # Increment view count
            cursor.execute(
                "UPDATE articles SET view_count = view_count + 1 WHERE id = %s",
                (article_id,)
            )
        
        article_response = ArticleResponse(**dict(article_record))
        return jsonify({
            'success': True,
            'article': article_response.dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Get article error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve article'
        }), 500


@articles_bp.route('/', methods=['POST'])
@auth_required
def create_article():
    """Create new article"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            article_data = ArticleCreate(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'details': e.errors()
            }), 400
        
        # Sanitize content
        sanitized_content = sanitize_html(article_data.content)
        
        # Calculate metrics
        reading_time = calculate_reading_time(sanitized_content)
        word_count = calculate_word_count(sanitized_content)
        seo_keywords = extract_keywords(sanitized_content)
        quality_score = calculate_quality_score(
            sanitized_content, 
            article_data.title, 
            article_data.summary
        )
        
        # Create article
        article_id = generate_uuid()
        author_id = request.current_user['id']
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                INSERT INTO articles (
                    id, title, content, summary, author_id, anonymous_author,
                    category, subcategory, tags, language, reading_time, word_count,
                    status, metadata, seo_keywords, quality_score, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING *
            """, (
                article_id, article_data.title, sanitized_content, article_data.summary,
                author_id, article_data.anonymous_author, article_data.category,
                article_data.subcategory, article_data.tags, article_data.language,
                reading_time, word_count, 'draft', article_data.metadata or {},
                seo_keywords, quality_score, 'now()', 'now()'
            ))
            
            article_record = cursor.fetchone()
        
        article_response = ArticleResponse(**dict(article_record))
        return jsonify({
            'success': True,
            'message': 'Article created successfully',
            'article': article_response.dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Create article error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to create article'
        }), 500


@articles_bp.route('/<article_id>', methods=['PUT'])
@auth_required
def update_article(article_id):
    """Update existing article"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            article_update = ArticleUpdate(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'details': e.errors()
            }), 400
        
        # Check if user owns the article or is admin
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT author_id FROM articles WHERE id = %s",
                (article_id,)
            )
            
            article = cursor.fetchone()
            if not article:
                return jsonify({
                    'success': False,
                    'message': 'Article not found'
                }), 404
            
            current_user_id = request.current_user['id']
            is_admin = request.current_user.get('role') == 'administrator'
            
            if article['author_id'] != current_user_id and not is_admin:
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            # Build update query
            update_fields = []
            params = []
            
            update_data = article_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'content' and value:
                    # Sanitize and recalculate metrics for content updates
                    sanitized_content = sanitize_html(value)
                    update_fields.extend([
                        "content = %s",
                        "reading_time = %s",
                        "word_count = %s"
                    ])
                    params.extend([
                        sanitized_content,
                        calculate_reading_time(sanitized_content),
                        calculate_word_count(sanitized_content)
                    ])
                elif field in ['title', 'summary', 'category', 'subcategory', 'tags', 'language', 'status', 'anonymous_author', 'metadata']:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return jsonify({
                    'success': False,
                    'message': 'No valid fields to update'
                }), 400
            
            update_fields.append("updated_at = %s")
            params.append('now()')
            
            # If publishing, set published_at
            if 'status' in update_data and update_data['status'] == 'published':
                update_fields.append("published_at = %s")
                params.append('now()')
            
            params.append(article_id)
            
            query = f"UPDATE articles SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cursor.execute(query, params)
            updated_article = cursor.fetchone()
        
        article_response = ArticleResponse(**dict(updated_article))
        return jsonify({
            'success': True,
            'message': 'Article updated successfully',
            'article': article_response.dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Update article error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to update article'
        }), 500


@articles_bp.route('/<article_id>', methods=['DELETE'])
@auth_required
def delete_article(article_id):
    """Delete article (soft delete by archiving)"""
    try:
        # Check if user owns the article or is admin
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT author_id FROM articles WHERE id = %s",
                (article_id,)
            )
            
            article = cursor.fetchone()
            if not article:
                return jsonify({
                    'success': False,
                    'message': 'Article not found'
                }), 404
            
            current_user_id = request.current_user['id']
            is_admin = request.current_user.get('role') == 'administrator'
            
            if article['author_id'] != current_user_id and not is_admin:
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            # Soft delete by archiving
            cursor.execute(
                "UPDATE articles SET status = 'archived', updated_at = %s WHERE id = %s",
                ('now()', article_id)
            )
        
        return jsonify({
            'success': True,
            'message': 'Article deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete article error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to delete article'
        }), 500


@articles_bp.route('/<article_id>/like', methods=['POST'])
@auth_required
def like_article(article_id):
    """Like an article"""
    try:
        user_id = request.current_user['id']
        
        with get_postgres_cursor() as cursor:
            # Check if already liked
            cursor.execute(
                "SELECT id FROM user_interactions WHERE user_id = %s AND article_id = %s AND interaction_type = 'like'",
                (user_id, article_id)
            )
            
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'Article already liked'
                }), 409
            
            # Add like interaction
            cursor.execute("""
                INSERT INTO user_interactions (
                    id, user_id, article_id, interaction_type, interaction_strength, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                generate_uuid(), user_id, article_id, 'like', 1.0, 'now()'
            ))
            
            # Update article like count
            cursor.execute(
                "UPDATE articles SET like_count = like_count + 1 WHERE id = %s",
                (article_id,)
            )
        
        return jsonify({
            'success': True,
            'message': 'Article liked successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Like article error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to like article'
        }), 500