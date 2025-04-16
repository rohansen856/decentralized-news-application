"""
Analytics routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.auth import auth_required
from shared.models import AnalyticsRequest, AnalyticsResponse

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)


@analytics_bp.route('/user/<user_id>', methods=['POST'])
@auth_required
def get_user_analytics(user_id):
    """Get user analytics data"""
    try:
        # Check permissions
        current_user_id = request.current_user.get('id')
        if user_id != current_user_id and request.current_user.get('role') != 'administrator':
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        data = request.get_json() or {}
        data['user_id'] = user_id
        
        try:
            analytics_data = AnalyticsRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False, 'message': 'Validation error', 'details': e.errors()
            }), 400
        
        with get_postgres_cursor() as cursor:
            metrics = {}
            
            # Date range
            date_from = analytics_data.date_from or (datetime.utcnow() - timedelta(days=30))
            date_to = analytics_data.date_to or datetime.utcnow()
            
            if 'views' in analytics_data.metrics:
                cursor.execute("""
                    SELECT COUNT(*) as view_count
                    FROM user_interactions 
                    WHERE user_id = %s AND interaction_type = 'view'
                    AND created_at BETWEEN %s AND %s
                """, (user_id, date_from, date_to))
                metrics['views'] = cursor.fetchone()['view_count']
            
            if 'likes' in analytics_data.metrics:
                cursor.execute("""
                    SELECT COUNT(*) as like_count
                    FROM user_interactions 
                    WHERE user_id = %s AND interaction_type = 'like'
                    AND created_at BETWEEN %s AND %s
                """, (user_id, date_from, date_to))
                metrics['likes'] = cursor.fetchone()['like_count']
            
            if 'shares' in analytics_data.metrics:
                cursor.execute("""
                    SELECT COUNT(*) as share_count
                    FROM user_interactions 
                    WHERE user_id = %s AND interaction_type = 'share'
                    AND created_at BETWEEN %s AND %s
                """, (user_id, date_from, date_to))
                metrics['shares'] = cursor.fetchone()['share_count']
        
        response = AnalyticsResponse(
            metrics=metrics,
            period={'from': date_from.isoformat(), 'to': date_to.isoformat()}
        )
        
        return jsonify(response.dict()), 200
    
    except Exception as e:
        logger.error(f"Get user analytics error: {e}")
        return jsonify({'success': False, 'message': 'Failed to get analytics'}), 500


@analytics_bp.route('/article/<article_id>', methods=['POST'])
def get_article_analytics(article_id):
    """Get article analytics data"""
    try:
        data = request.get_json() or {}
        data['article_id'] = article_id
        
        try:
            analytics_data = AnalyticsRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False, 'message': 'Validation error', 'details': e.errors()
            }), 400
        
        with get_postgres_cursor() as cursor:
            # Check if article exists and user has permission
            cursor.execute("SELECT author_id FROM articles WHERE id = %s", (article_id,))
            article = cursor.fetchone()
            
            if not article:
                return jsonify({'success': False, 'message': 'Article not found'}), 404
            
            # Basic analytics available to everyone, detailed to author only
            metrics = {}
            date_from = analytics_data.date_from or (datetime.utcnow() - timedelta(days=30))
            date_to = analytics_data.date_to or datetime.utcnow()
            
            # Basic metrics
            cursor.execute("""
                SELECT view_count, like_count, share_count, comment_count,
                       engagement_score, quality_score, trending_score
                FROM articles WHERE id = %s
            """, (article_id,))
            
            article_stats = cursor.fetchone()
            if article_stats:
                metrics.update(dict(article_stats))
            
            # Interaction metrics over time period
            if 'views' in analytics_data.metrics:
                cursor.execute("""
                    SELECT COUNT(*) as period_views
                    FROM user_interactions 
                    WHERE article_id = %s AND interaction_type = 'view'
                    AND created_at BETWEEN %s AND %s
                """, (article_id, date_from, date_to))
                metrics['period_views'] = cursor.fetchone()['period_views']
        
        response = AnalyticsResponse(
            metrics=metrics,
            period={'from': date_from.isoformat(), 'to': date_to.isoformat()}
        )
        
        return jsonify(response.dict()), 200
    
    except Exception as e:
        logger.error(f"Get article analytics error: {e}")
        return jsonify({'success': False, 'message': 'Failed to get analytics'}), 500