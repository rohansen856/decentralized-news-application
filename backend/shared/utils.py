"""
Shared utility functions for both Flask and FastAPI backends
"""

import re
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


def generate_uuid() -> str:
    """Generate UUID4 string"""
    return str(uuid.uuid4())


def calculate_reading_time(content: str) -> int:
    """Calculate estimated reading time in minutes (assuming 200 WPM)"""
    word_count = len(content.split())
    reading_time = max(1, round(word_count / 200))  # At least 1 minute
    return reading_time


def calculate_word_count(content: str) -> int:
    """Calculate word count of content"""
    return len(content.split())


def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from content (simple implementation)"""
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                  'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
                  'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                  'would', 'could', 'should', 'can', 'may', 'might', 'this', 
                  'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 
                  'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    # Extract words (alphanumeric only)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    
    # Filter stop words and count occurrences
    word_count = {}
    for word in words:
        if word not in stop_words:
            word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]


def calculate_engagement_score(views: int, likes: int, shares: int, comments: int, 
                             reading_time: int, time_spent_avg: float) -> float:
    """Calculate engagement score based on various metrics"""
    if views == 0:
        return 0.0
    
    # Normalize metrics
    like_rate = likes / views if views > 0 else 0
    share_rate = shares / views if views > 0 else 0
    comment_rate = comments / views if views > 0 else 0
    completion_rate = min(time_spent_avg / (reading_time * 60), 1.0) if reading_time > 0 else 0
    
    # Weighted score calculation
    engagement_score = (
        like_rate * 0.3 +
        share_rate * 0.3 +
        comment_rate * 0.2 +
        completion_rate * 0.2
    ) * 100
    
    return round(engagement_score, 2)


def calculate_quality_score(content: str, title: str, summary: Optional[str] = None) -> float:
    """Calculate content quality score based on various factors"""
    score = 0.0
    
    # Content length score (0-30 points)
    word_count = calculate_word_count(content)
    if word_count >= 500:
        score += 30
    elif word_count >= 300:
        score += 20
    elif word_count >= 150:
        score += 10
    
    # Title quality score (0-20 points)
    title_word_count = len(title.split())
    if 5 <= title_word_count <= 12:
        score += 20
    elif 3 <= title_word_count <= 15:
        score += 15
    else:
        score += 5
    
    # Summary presence score (0-15 points)
    if summary and len(summary.strip()) > 50:
        score += 15
    elif summary:
        score += 10
    
    # Readability score (0-20 points) - Simple sentence length check
    sentences = content.split('.')
    if sentences:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 10 <= avg_sentence_length <= 20:
            score += 20
        elif 5 <= avg_sentence_length <= 25:
            score += 15
        else:
            score += 10
    
    # Structure score (0-15 points) - Check for paragraphs
    paragraphs = content.split('\n\n')
    if len(paragraphs) >= 3:
        score += 15
    elif len(paragraphs) >= 2:
        score += 10
    else:
        score += 5
    
    return round(min(score, 100.0), 2)


def calculate_trending_score(views: int, likes: int, shares: int, comments: int,
                           published_at: datetime, current_time: datetime = None) -> float:
    """Calculate trending score based on recent activity and recency"""
    if current_time is None:
        current_time = datetime.now()
    
    # Time decay factor (more recent = higher score)
    hours_since_published = (current_time - published_at).total_seconds() / 3600
    if hours_since_published <= 1:
        time_factor = 1.0
    elif hours_since_published <= 24:
        time_factor = 0.8
    elif hours_since_published <= 72:
        time_factor = 0.6
    elif hours_since_published <= 168:  # 1 week
        time_factor = 0.4
    else:
        time_factor = 0.1
    
    # Activity score
    activity_score = (views * 0.1 + likes * 2 + shares * 3 + comments * 2.5)
    
    # Apply time decay
    trending_score = activity_score * time_factor
    
    return round(trending_score, 2)


def sanitize_html(content: str) -> str:
    """Basic HTML sanitization (remove dangerous tags)"""
    # Simple implementation - in production, use a proper HTML sanitizer
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
    for tag in dangerous_tags:
        content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(f'<{tag}[^>]*/?>', '', content, flags=re.IGNORECASE)
    return content


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_session_id(user_id: str, timestamp: datetime = None) -> str:
    """Generate unique session ID"""
    if timestamp is None:
        timestamp = datetime.now()
    
    session_data = f"{user_id}:{timestamp.isoformat()}:{uuid.uuid4()}"
    return hashlib.sha256(session_data.encode()).hexdigest()


def paginate_query_results(results: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Paginate query results"""
    total = len(results)
    pages = (total + per_page - 1) // per_page  # Ceiling division
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'data': results[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': pages,
        'has_next': page < pages,
        'has_prev': page > 1
    }


def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format"""
    return dt.isoformat() if dt else None


def deserialize_datetime(dt_str: str) -> Optional[datetime]:
    """Deserialize datetime from ISO format"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return None


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON with fallback"""
    try:
        return json.loads(json_str) if json_str else default
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any) -> str:
    """Safely dump JSON with datetime handling"""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    try:
        return json.dumps(obj, default=json_serializer)
    except TypeError:
        return "{}"


def cache_key_generator(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            key_parts.append(','.join(str(x) for x in arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}={value}")
    
    # Create hash of combined key
    key_string = ':'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def health_check_service(service_name: str, check_function) -> Dict[str, str]:
    """Check health of a service"""
    try:
        check_function()
        return {service_name: "healthy"}
    except Exception as e:
        return {service_name: f"unhealthy - {str(e)}"}


class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds() * 1000  # milliseconds
    
    def get_duration_ms(self) -> float:
        """Get duration in milliseconds"""
        return self.duration if self.duration is not None else 0.0