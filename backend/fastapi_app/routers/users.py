"""
User management routes for FastAPI backend
"""

import sys
import os
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import UserUpdate, UserResponse, PaginatedResponse
from shared.utils import paginate_query_results
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    role: str = Query(""),
    admin_user: dict = Depends(get_admin_user)
):
    """Get list of users (admin only)"""
    try:
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
        
        return PaginatedResponse(**paginated)
    
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user by ID"""
    try:
        # Users can only view their own profile unless they're admin
        if user_id != current_user.get('id') and current_user.get('role') != 'administrator':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND is_active = true",
                (user_id,)
            )
            
            user_record = cursor.fetchone()
            if not user_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        return UserResponse(**dict(user_record))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, 
    user_update: UserUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Update user information"""
    try:
        # Users can only update their own profile unless they're admin
        is_admin = current_user.get('role') == 'administrator'
        if user_id != current_user.get('id') and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Build update query
        update_fields = []
        params = []
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['username', 'email', 'role', 'anonymous_mode', 'profile_data', 'preferences']:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Non-admin users cannot change role
        if 'role' in update_data and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change role"
            )
        
        update_fields.append("updated_at = %s")
        params.append('now()')
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
        
        with get_postgres_cursor() as cursor:
            cursor.execute(query, params)
            updated_user = cursor.fetchone()
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        return UserResponse(**dict(updated_user))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete user (soft delete)"""
    try:
        # Users can delete their own account, admins can delete any
        if user_id != current_user.get('id') and current_user.get('role') != 'administrator':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        with get_postgres_cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = false, updated_at = %s WHERE id = %s RETURNING id",
                ('now()', user_id)
            )
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        return {"success": True, "message": "User deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )