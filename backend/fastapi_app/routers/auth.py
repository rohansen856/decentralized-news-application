"""
Authentication routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends, status
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.auth import auth_manager, hash_password, verify_password
from shared.models import UserCreate, UserLogin, UserResponse, TokenResponse, BaseResponse
from shared.utils import generate_uuid, validate_email
from ..dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (user_data.email, user_data.username)
            )
            
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email or username already exists"
                )
            
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
                user_data.profile_data or {}, user_data.preferences or {},
                'now()', 'now()', 'now()'
            ))
            
            user_record = cursor.fetchone()
        
        # Create response
        user_response = UserResponse(**dict(user_record))
        access_token = auth_manager.create_access_token(dict(user_record))
        
        return TokenResponse(
            access_token=access_token,
            expires_in=auth_manager.access_token_expires,
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """Login user and return JWT token"""
    try:
        # Check user credentials
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND is_active = true",
                (login_data.email,)
            )
            
            user_record = cursor.fetchone()
            
            if not user_record or not verify_password(login_data.password, user_record['password_hash']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Update last active
            cursor.execute(
                "UPDATE users SET last_active = %s WHERE id = %s",
                ('now()', user_record['id'])
            )
        
        # Create response
        user_response = UserResponse(**dict(user_record))
        access_token = auth_manager.create_access_token(dict(user_record))
        
        return TokenResponse(
            access_token=access_token,
            expires_in=auth_manager.access_token_expires,
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)


@router.post("/refresh", response_model=BaseResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    try:
        # Create new token
        new_token = auth_manager.create_access_token(current_user)
        
        return {
            'success': True,
            'access_token': new_token,
            'token_type': 'bearer',
            'expires_in': auth_manager.access_token_expires
        }
    
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )