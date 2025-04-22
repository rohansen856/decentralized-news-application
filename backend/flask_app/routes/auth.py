"""
Authentication routes for Flask backend
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.auth import auth_manager, hash_password, verify_password
from shared.models import UserCreate, UserLogin, UserResponse, TokenResponse
from shared.utils import generate_uuid, validate_email

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            user_data = UserCreate(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'details': e.errors()
            }), 400
        
        # Check if user already exists
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (user_data.email, user_data.username)
            )
            
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'User with this email or username already exists'
                }), 409
            
            # Create new user
            user_id = generate_uuid()
            hashed_password = hash_password(user_data.password)
            
            cursor.execute("""
                INSERT INTO users (
                    id, username, email, password_hash, role, anonymous_mode,
                    profile_data, preferences, created_at, updated_at, last_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                user_id, user_data.username, user_data.email, hashed_password,
                user_data.role.value, user_data.anonymous_mode,
                json.dumps(user_data.profile_data or {}), json.dumps(user_data.preferences or {}),
                'now()', 'now()', 'now()'
            ))
            
            user_record = cursor.fetchone()
        
        # Create response
        user_response = UserResponse(**dict(user_record))
        access_token = auth_manager.create_access_token(dict(user_record))
        
        return jsonify(TokenResponse(
            access_token=access_token,
            expires_in=auth_manager.access_token_expires,
            user=user_response
        ).dict()), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error_code': 'REGISTRATION_ERROR'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate input
        try:
            login_data = UserLogin(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'details': e.errors()
            }), 400
        
        # Check user credentials
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND is_active = true",
                (login_data.email,)
            )
            
            user_record = cursor.fetchone()
            
            if not user_record or not verify_password(login_data.password, user_record['password_hash']):
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials'
                }), 401
            
            # Update last active
            cursor.execute(
                "UPDATE users SET last_active = %s WHERE id = %s",
                ('now()', user_record['id'])
            )
        
        # Create response
        user_response = UserResponse(**dict(user_record))
        access_token = auth_manager.create_access_token(dict(user_record))
        
        return jsonify(TokenResponse(
            access_token=access_token,
            expires_in=auth_manager.access_token_expires,
            user=user_response
        ).dict()), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error_code': 'LOGIN_ERROR'
        }), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        # Extract token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': 'Authorization header required'}), 401
        
        token = auth_manager.extract_token_from_header(auth_header)
        if not token:
            return jsonify({'success': False, 'message': 'Invalid authorization header'}), 401
        
        # Verify token and get user data
        user_data = auth_manager.get_user_from_token(token)
        if not user_data:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
        
        # Get fresh user data from database
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND is_active = true",
                (user_data['id'],)
            )
            
            user_record = cursor.fetchone()
            if not user_record:
                return jsonify({'success': False, 'message': 'User not found'}), 404
        
        user_response = UserResponse(**dict(user_record))
        return jsonify({
            'success': True,
            'user': user_response.dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get user information',
            'error_code': 'GET_USER_ERROR'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token"""
    try:
        # Extract token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': 'Authorization header required'}), 401
        
        token = auth_manager.extract_token_from_header(auth_header)
        if not token:
            return jsonify({'success': False, 'message': 'Invalid authorization header'}), 401
        
        # Verify current token
        user_data = auth_manager.get_user_from_token(token)
        if not user_data:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
        
        # Get fresh user data from database
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND is_active = true",
                (user_data['id'],)
            )
            
            user_record = cursor.fetchone()
            if not user_record:
                return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Create new token
        new_token = auth_manager.create_access_token(dict(user_record))
        
        return jsonify({
            'success': True,
            'access_token': new_token,
            'token_type': 'bearer',
            'expires_in': auth_manager.access_token_expires
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'message': 'Token refresh failed',
            'error_code': 'REFRESH_ERROR'
        }), 500