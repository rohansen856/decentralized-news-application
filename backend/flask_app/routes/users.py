"""
User management routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.auth import auth_required, admin_required
from shared.models import UserUpdate, UserResponse
from shared.utils import paginate_query_results

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)


@users_bp.route('/', methods=['GET'])
@auth_required
def get_users():
    """Get list of users (admin only for full list)"""
    try:
        # Pagination parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        
        # Check if current user is admin
        is_admin = request.current_user.get('role') == 'administrator'
        
        if not is_admin:
            return jsonify({
                'success': False,
                'message': 'Administrator privileges required'
            }), 403
        
        # Build query
        query = "SELECT * FROM users WHERE is_active = true"
        params = []
        
        if search:
            query += " AND (username ILIKE %s OR email ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if role:
            query += " AND role = %s"
            params.append(role)
        
        query += " ORDER BY created_at DESC"
        
        with get_postgres_cursor() as cursor:
            cursor.execute(query, params)
            users = cursor.fetchall()
        
        # Convert to response objects
        user_responses = [UserResponse(**dict(user)) for user in users]
        
        # Paginate results
        paginated = paginate_query_results([u.dict() for u in user_responses], page, per_page)
        
        return jsonify({
            'success': True,
            **paginated
        }), 200
    
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve users'
        }), 500


@users_bp.route('/<user_id>', methods=['GET'])
@auth_required
def get_user(user_id):
    """Get user by ID"""
    try:
        # Users can only view their own profile unless they're admin
        current_user_id = request.current_user.get('id')
        is_admin = request.current_user.get('role') == 'administrator'
        
        if user_id != current_user_id and not is_admin:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND is_active = true",
                (user_id,)
            )
            
            user_record = cursor.fetchone()
            if not user_record:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
        
        user_response = UserResponse(**dict(user_record))
        return jsonify({
            'success': True,
            'user': user_response.dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve user'
        }), 500


@users_bp.route('/<user_id>', methods=['PUT'])
@auth_required
def update_user(user_id):
    """Update user information"""
    try:
        # Users can only update their own profile unless they're admin
        current_user_id = request.current_user.get('id')
        is_admin = request.current_user.get('role') == 'administrator'
        
        if user_id != current_user_id and not is_admin:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            user_update = UserUpdate(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'details': e.errors()
            }), 400
        
        # Build update query
        update_fields = []
        params = []
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['username', 'email', 'role', 'anonymous_mode', 'profile_data', 'preferences']:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            return jsonify({
                'success': False,
                'message': 'No valid fields to update'
            }), 400
        
        # Non-admin users cannot change role
        if 'role' in update_data and not is_admin:
            return jsonify({
                'success': False,
                'message': 'Cannot change role'
            }), 403
        
        update_fields.append("updated_at = %s")
        params.append('now()')
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
        
        with get_postgres_cursor() as cursor:
            cursor.execute(query, params)
            updated_user = cursor.fetchone()
            
            if not updated_user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
        
        user_response = UserResponse(**dict(updated_user))
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user_response.dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Update user error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to update user'
        }), 500


@users_bp.route('/<user_id>', methods=['DELETE'])
@auth_required
def delete_user(user_id):
    """Delete user (soft delete by setting is_active to false)"""
    try:
        # Users can delete their own account, admins can delete any
        current_user_id = request.current_user.get('id')
        is_admin = request.current_user.get('role') == 'administrator'
        
        if user_id != current_user_id and not is_admin:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = false, updated_at = %s WHERE id = %s RETURNING id",
                ('now()', user_id)
            )
            
            result = cursor.fetchone()
            if not result:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to delete user'
        }), 500


@users_bp.route('/<user_id>/preferences', methods=['GET'])
@auth_required
def get_user_preferences(user_id):
    """Get user preferences"""
    try:
        current_user_id = request.current_user.get('id')
        
        if user_id != current_user_id:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM user_preferences WHERE user_id = %s",
                (user_id,)
            )
            
            preferences = cursor.fetchone()
            if not preferences:
                return jsonify({
                    'success': False,
                    'message': 'Preferences not found'
                }), 404
        
        return jsonify({
            'success': True,
            'preferences': dict(preferences)
        }), 200
    
    except Exception as e:
        logger.error(f"Get user preferences error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve preferences'
        }), 500