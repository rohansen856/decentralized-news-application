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
            date_from = analytics_data.date_from or (datetime.now() - timedelta(days=30))
            date_to = analytics_data.date_to or datetime.now()
            
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


@router.get("/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    try:
        if current_user.get('role') != 'administrator':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        with get_postgres_cursor() as cursor:
            # Get total users
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_active = true")
            total_users = cursor.fetchone()['total'] or 0
            
            # Get new users today
            cursor.execute("""
                SELECT COUNT(*) as new_today FROM users 
                WHERE is_active = true AND DATE(created_at) = CURRENT_DATE
            """)
            new_users_today = cursor.fetchone()['new_today'] or 0
            
            # Get total articles
            cursor.execute("SELECT COUNT(*) as total FROM articles WHERE status = 'published'")
            total_articles = cursor.fetchone()['total'] or 0
            
            # Get pending reviews (draft articles)
            cursor.execute("SELECT COUNT(*) as pending FROM articles WHERE status = 'draft'")
            pending_reviews = cursor.fetchone()['pending'] or 0
            
            # Get flagged content (placeholder - not implemented in schema)
            flagged_content = 0
            
            # Get active users (users with activity in last 24h)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as active FROM user_interactions 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            active_users = cursor.fetchone()['active'] or 0
            
            # Get recent activity stats
            cursor.execute("""
                SELECT COUNT(*) as articles_week FROM articles 
                WHERE status = 'published' AND created_at >= NOW() - INTERVAL '7 days'
            """)
            articles_this_week = cursor.fetchone()['articles_week'] or 0
            
            return {
                "success": True,
                "stats": {
                    "totalUsers": total_users,
                    "totalArticles": total_articles,
                    "pendingReviews": pending_reviews,
                    "flaggedContent": flagged_content,
                    "activeUsers": active_users,
                    "newUsersToday": new_users_today,
                    "articlesThisWeek": articles_this_week
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get admin stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get admin statistics")


@router.get("/admin/recent-users")
async def get_recent_users(current_user: dict = Depends(get_current_user)):
    """Get recent user registrations"""
    try:
        if current_user.get('role') != 'administrator':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        with get_postgres_cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, role, created_at, is_active
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            users = cursor.fetchall()
            
            recent_users = []
            for user in users:
                recent_users.append({
                    "id": user['id'],
                    "name": user['username'],
                    "email": user['email'],
                    "role": user['role'],
                    "joinDate": user['created_at'].strftime('%Y-%m-%d') if user['created_at'] else '',
                    "status": "active" if user['is_active'] else "inactive"
                })
            
            return {"success": True, "users": recent_users}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recent users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent users")


@router.get("/admin/flagged-content")
async def get_flagged_content(current_user: dict = Depends(get_current_user)):
    """Get flagged content for moderation"""
    try:
        if current_user.get('role') != 'administrator':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        with get_postgres_cursor() as cursor:
            # For now, return articles with low quality scores as "flagged"
            cursor.execute("""
                SELECT a.id, a.title, u.username as author, a.created_at, a.quality_score
                FROM articles a
                JOIN users u ON a.author_id = u.id
                WHERE a.quality_score < 0.5 OR a.status = 'under_review'
                ORDER BY a.created_at DESC 
                LIMIT 10
            """)
            flagged = cursor.fetchall()
            
            flagged_content = []
            for item in flagged:
                flagged_content.append({
                    "id": item['id'],
                    "title": item['title'],
                    "author": item['author'],
                    "reason": "Low quality score" if item['quality_score'] < 0.5 else "Under review",
                    "date": item['created_at'].strftime('%Y-%m-%d') if item['created_at'] else ''
                })
            
            return {"success": True, "content": flagged_content}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get flagged content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get flagged content")