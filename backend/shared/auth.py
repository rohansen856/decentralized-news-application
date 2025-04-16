"""
Shared authentication utilities for both Flask and FastAPI backends
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
import uuid


class AuthManager:
    """Centralized authentication management"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key')
        self.jwt_algorithm = 'HS256'
        self.access_token_expires = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
        self.bcrypt_rounds = int(os.getenv('BCRYPT_ROUNDS', 12))
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        payload = {
            'user_id': str(user_data['id']),
            'username': user_data['username'],
            'email': user_data['email'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expires),
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())  # JWT ID for token revocation
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """Extract token from Authorization header"""
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user data from token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return {
            'id': payload.get('user_id'),
            'username': payload.get('username'),
            'email': payload.get('email'),
            'role': payload.get('role')
        }


# Global auth manager instance
auth_manager = AuthManager()


# Convenience functions
def hash_password(password: str) -> str:
    return auth_manager.hash_password(password)

def verify_password(password: str, hashed: str) -> bool:
    return auth_manager.verify_password(password, hashed)

def create_access_token(user_data: Dict[str, Any]) -> str:
    return auth_manager.create_access_token(user_data)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    return auth_manager.verify_token(token)

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    return auth_manager.get_user_from_token(token)


# Decorators for route protection
def auth_required(f):
    """Decorator for Flask routes requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        token = auth_manager.extract_token_from_header(auth_header)
        if not token:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        user_data = auth_manager.get_user_from_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user data to request context
        request.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """Decorator for Flask routes requiring admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        if not hasattr(request, 'current_user'):
            return jsonify({'error': 'Authentication required'}), 401
        
        if request.current_user.get('role') != 'administrator':
            return jsonify({'error': 'Administrator privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function