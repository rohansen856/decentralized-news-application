"""
User interactions routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends, status
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import InteractionCreate, InteractionResponse
from shared.utils import generate_uuid, generate_session_id
from ..dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(interaction_data: InteractionCreate, current_user: dict = Depends(get_current_user)):
    """Record user interaction with article"""
    try:
        user_id = current_user['id']
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
        
        return InteractionResponse(**dict(interaction_record))
    except Exception as e:
        logger.error(f"Create interaction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")