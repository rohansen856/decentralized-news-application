"""
Authentication routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor, prepare_json_data
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
            
            # Prepare JSON data properly for PostgreSQL
            profile_data = prepare_json_data(user_data.profile_data or {})
            preferences = prepare_json_data(user_data.preferences or {})
            
            cursor.execute("""
                INSERT INTO users (
                    id, username, email, password_hash, role, anonymous_mode,
                    profile_data, preferences, created_at, updated_at, last_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                user_id, 
                user_data.username, 
                user_data.email, 
                hashed_password,
                user_data.role.value, 
                user_data.anonymous_mode,
                profile_data,  # Now properly prepared for PostgreSQL
                preferences,   # Now properly prepared for PostgreSQL
                datetime.now(), 
                datetime.now(), 
                datetime.now()
            ))
            
            user_record = cursor.fetchone()
            
            if not user_record:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
        
        # Create response
        user_response = UserResponse(**dict(user_record))
        access_token = auth_manager.create_access_token(dict(user_record))
        
        logger.info(f"User registered successfully: {user_data.username} ({user_data.email})")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=auth_manager.access_token_expires,
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
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
                (datetime.now(), user_record['id'])
            )
        
        # Create response
        user_response = UserResponse(**dict(user_record))
        access_token = auth_manager.create_access_token(dict(user_record))
        
        logger.info(f"User logged in successfully: {user_record['username']}")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=auth_manager.access_token_expires,
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
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
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: dict, 
    current_user: dict = Depends(get_current_user)
):
    """Update user profile data"""
    try:
        with get_postgres_cursor() as cursor:
            # Prepare JSON data properly
            prepared_profile_data = prepare_json_data(profile_data)
            
            cursor.execute("""
                UPDATE users 
                SET profile_data = %s, updated_at = %s 
                WHERE id = %s
                RETURNING *
            """, (
                prepared_profile_data,
                datetime.now(),
                current_user['id']
            ))
            
            updated_user = cursor.fetchone()
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        logger.info(f"Profile updated for user: {current_user['username']}")
        return UserResponse(**dict(updated_user))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.put("/preferences", response_model=UserResponse)
async def update_preferences(
    preferences_data: dict, 
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        with get_postgres_cursor() as cursor:
            # Prepare JSON data properly
            prepared_preferences = prepare_json_data(preferences_data)
            
            cursor.execute("""
                UPDATE users 
                SET preferences = %s, updated_at = %s 
                WHERE id = %s
                RETURNING *
            """, (
                prepared_preferences,
                datetime.now(),
                current_user['id']
            ))
            
            updated_user = cursor.fetchone()
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        logger.info(f"Preferences updated for user: {current_user['username']}")
        return UserResponse(**dict(updated_user))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preferences update error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Preferences update failed"
        )


@router.get("/test-db")
async def test_database_connection():
    """Test database connection - useful for debugging"""
    try:
        with get_postgres_cursor() as cursor:
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
            
            if result and result['test_value'] == 1:
                return {
                    "message": "Database connection successful",
                    "timestamp": datetime.now().isoformat(),
                    "status": "healthy"
                }
            else:
                raise Exception("Unexpected database response")
                
    except Exception as e:
        logger.error(f"Database test error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )