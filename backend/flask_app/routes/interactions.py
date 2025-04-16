"""
User interactions routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.auth import auth_required
from shared.models import InteractionCreate, InteractionResponse
from shared.utils import generate_uuid, generate_session_id

interactions_bp = Blueprint('interactions', __name__)
logger = logging.getLogger(__name__)


@interactions_bp.route('/', methods=['POST'])
@auth_required
def create_interaction():
    """Record user interaction with article"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            interaction_data = InteractionCreate(**data)
        except ValidationError as e:
            return jsonify({
                'success': False, 'message': 'Validation error', 'details': e.errors()
            }), 400
        
        user_id = request.current_user['id']
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
                interaction_data.device_type, interaction_data.context_data or {},
                session_id, 'now()'
            ))
            
            interaction_record = cursor.fetchone()
        
        response = InteractionResponse(**dict(interaction_record))
        return jsonify({'success': True, 'interaction': response.dict()}), 201
    
    except Exception as e:
        logger.error(f"Create interaction error: {e}")
        return jsonify({'success': False, 'message': 'Failed to record interaction'}), 500


@interactions_bp.route('/user/<user_id>', methods=['GET'])
@auth_required
def get_user_interactions(user_id):
    """Get user interactions"""
    try:
        current_user_id = request.current_user.get('id')
        if user_id != current_user_id and request.current_user.get('role') != 'administrator':
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                SELECT ui.*, a.title as article_title 
                FROM user_interactions ui 
                JOIN articles a ON ui.article_id = a.id 
                WHERE ui.user_id = %s ORDER BY ui.created_at DESC LIMIT 100
            """, (user_id,))
            
            interactions = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'interactions': [dict(i) for i in interactions]
        }), 200
    
    except Exception as e:
        logger.error(f"Get user interactions error: {e}")
        return jsonify({'success': False, 'message': 'Failed to retrieve interactions'}), 500