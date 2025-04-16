"""
Shared data models and schemas for both Flask and FastAPI backends
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
import uuid


# Enums
class UserRole(str, Enum):
    AUTHOR = "author"
    READER = "reader"
    ADMINISTRATOR = "administrator"
    AUDITOR = "auditor"


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class InteractionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SAVE = "save"
    SHARE = "share"
    VIEW = "view"
    COMMENT = "comment"


class RecommendationModel(str, Enum):
    TWO_TOWER = "two_tower"
    CNN = "cnn"
    RNN = "rnn"
    GNN = "gnn"
    ATTENTION = "attention"
    HYBRID = "hybrid"


# Base models
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# User models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.READER
    anonymous_mode: bool = False
    profile_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    anonymous_mode: Optional[bool] = None
    profile_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    id: uuid.UUID
    did_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_active: datetime
    is_active: bool
    verification_status: bool
    reputation_score: float
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseResponse):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# Article models
class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    language: str = Field(default="en", max_length=10)
    anonymous_author: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    language: Optional[str] = Field(None, max_length=10)
    status: Optional[ArticleStatus] = None
    anonymous_author: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ArticleResponse(ArticleBase):
    id: uuid.UUID
    author_id: Optional[uuid.UUID] = None
    status: ArticleStatus
    reading_time: int
    word_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    source_url: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    seo_keywords: List[str] = Field(default_factory=list)
    engagement_score: float
    quality_score: float
    trending_score: float
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Interaction models
class InteractionCreate(BaseModel):
    article_id: uuid.UUID
    interaction_type: InteractionType
    interaction_strength: float = Field(default=1.0, ge=0.0, le=1.0)
    reading_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    time_spent: int = Field(default=0, ge=0)
    device_type: str = Field(default="unknown")
    context_data: Optional[Dict[str, Any]] = None


class InteractionResponse(InteractionCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    session_id: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Recommendation models
class RecommendationRequest(BaseModel):
    user_id: uuid.UUID
    limit: int = Field(default=20, ge=1, le=100)
    categories: Optional[List[str]] = None
    exclude_read: bool = True
    diversity_weight: float = Field(default=0.3, ge=0.0, le=1.0)


class RecommendationResponse(BaseResponse):
    recommendations: List[ArticleResponse]
    model_used: str
    generated_at: datetime
    expires_at: datetime


# Search models
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    categories: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    author_id: Optional[uuid.UUID] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="relevance")  # relevance, date, popularity


class SearchResponse(BaseResponse):
    results: List[ArticleResponse]
    total_count: int
    query: str
    execution_time_ms: float


# Analytics models
class AnalyticsRequest(BaseModel):
    user_id: Optional[uuid.UUID] = None
    article_id: Optional[uuid.UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    metrics: List[str] = Field(default_factory=lambda: ["views", "likes", "shares"])


class AnalyticsResponse(BaseResponse):
    metrics: Dict[str, Any]
    period: Dict[str, Any]


# Pagination models
class PaginatedResponse(BaseResponse):
    data: List[Any]
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


# Health check model
class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)
    version: str = "1.0.0"