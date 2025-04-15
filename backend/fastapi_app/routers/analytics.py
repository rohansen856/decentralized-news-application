"""
Analytics routes for FastAPI backend
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.database import get_postgres_cursor
from shared.models import AnalyticsRequest, AnalyticsResponse
from ..dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/user/{user_id}", response_model=AnalyticsResponse)
async def get_user_analytics(user_id: str, analytics_data: AnalyticsRequest, current_user: dict = Depends(get_current_user)):
    """Get user analytics data"""
    try:
        if user_id != current_user.get('id') and current_user.get('role') != 'administrator':
            raise HTTPException(status_code=403, detail="Access denied")
        
        with get_postgres_cursor() as cursor:
            metrics = {}
            date_from = analytics_data.date_from or (datetime.utcnow() - timedelta(days=30))
            date_to = analytics_data.date_to or datetime.utcnow()
            
            if 'views' in analytics_data.metrics:
                cursor.execute("""
                    SELECT COUNT(*) as view_count FROM user_interactions 
                    WHERE user_id = %s AND interaction_type = 'view' AND created_at BETWEEN %s AND %s
                """, (user_id, date_from, date_to))
                metrics['views'] = cursor.fetchone()['view_count']
            
            if 'likes' in analytics_data.metrics:
                cursor.execute("""
                    SELECT COUNT(*) as like_count FROM user_interactions 
                    WHERE user_id = %s AND interaction_type = 'like' AND created_at BETWEEN %s AND %s
                """, (user_id, date_from, date_to))
                metrics['likes'] = cursor.fetchone()['like_count']
        
        return AnalyticsResponse(
            metrics=metrics,
            period={'from': date_from.isoformat(), 'to': date_to.isoformat()}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")