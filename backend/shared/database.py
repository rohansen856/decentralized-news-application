"""
Shared database connection utilities for both Flask and FastAPI backends
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import psycopg2.extras
from pymongo import MongoClient
import redis
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

# Register JSON adapter for PostgreSQL
psycopg2.extras.register_default_json(globally=True)
psycopg2.extras.register_default_jsonb(globally=True)


class DatabaseManager:
    """Centralized database connection management"""
    
    def __init__(self):
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'news_app'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password'),
        }
        
        self.mongodb_config = {
            'host': os.getenv('MONGODB_HOST', 'localhost'),
            'port': int(os.getenv('MONGODB_PORT', 27017)),
            'username': os.getenv('MONGODB_USER', 'admin'),
            'password': os.getenv('MONGODB_PASSWORD', 'password'),
            'database': os.getenv('MONGODB_DB', 'news_app')
        }
        
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0)),
            'password': os.getenv('REDIS_PASSWORD', "redis_password"),
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True
        }
        
        # Initialize connections
        self._postgres_pool = None
        self._mongodb_client = None
        self._redis_client = None
    
    @contextmanager
    def get_postgres_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """Get PostgreSQL connection with automatic cleanup"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            conn.autocommit = False
            # Set session timezone
            with conn.cursor() as cursor:
                cursor.execute("SET timezone = 'UTC'")
            yield conn
        except psycopg2.Error as e:
            if conn:
                try:
                    conn.rollback()
                except psycopg2.Error:
                    pass  # Connection might be closed
            logger.error(f"PostgreSQL connection error: {e}")
            raise
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except psycopg2.Error:
                    pass
            logger.error(f"PostgreSQL connection error: {e}")
            raise
        finally:
            if conn and not conn.closed:
                conn.close()
    
    @contextmanager
    def get_postgres_cursor(self) -> Generator[RealDictCursor, None, None]:
        """Get PostgreSQL cursor with automatic cleanup"""
        with self.get_postgres_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                yield cursor
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                logger.error(f"PostgreSQL cursor error: {e}")
                raise
            except Exception as e:
                conn.rollback()
                logger.error(f"PostgreSQL cursor error: {e}")
                raise
            finally:
                if cursor and not cursor.closed:
                    cursor.close()
    
    def prepare_json_data(self, data: Any) -> Any:
        """
        Prepare data for PostgreSQL insertion, handling dictionaries and lists
        """
        if isinstance(data, dict):
            # Use psycopg2's Json adapter for JSONB columns
            return Json(data)
        elif isinstance(data, list):
            # Handle lists that might contain dictionaries
            return Json(data)
        elif data is None:
            return None
        else:
            # For other types, try to JSON serialize to check if it's valid
            try:
                json.dumps(data)
                return data
            except (TypeError, ValueError):
                # If it can't be serialized, convert to string
                return str(data)
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[list]:
        """
        Execute a query with proper error handling and JSON support
        """
        with self.get_postgres_cursor() as cursor:
            try:
                # Process parameters to handle dictionaries
                if params:
                    processed_params = tuple(
                        self.prepare_json_data(param) if isinstance(param, (dict, list)) else param 
                        for param in params
                    )
                else:
                    processed_params = None
                
                cursor.execute(query, processed_params)
                
                if fetch:
                    return cursor.fetchall()
                return None
                
            except psycopg2.Error as e:
                logger.error(f"Query execution error: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    def insert_user(self, user_data: Dict[str, Any]) -> int:
        """
        Example method showing how to insert user data with JSON fields
        """
        query = """
            INSERT INTO users (username, email, password_hash, metadata, preferences, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """
        
        # Prepare the data
        params = (
            user_data.get('username'),
            user_data.get('email'),
            user_data.get('password_hash'),
            user_data.get('metadata', {}),  # This will be handled as JSON
            user_data.get('preferences', {})  # This will be handled as JSON
        )
        
        result = self.execute_query(query, params, fetch=True)
        return result[0]['id'] if result else None
    
    def get_mongodb_client(self) -> MongoClient:
        """Get MongoDB client (singleton pattern)"""
        if self._mongodb_client is None:
            try:
                if self.mongodb_config['username'] and self.mongodb_config['password']:
                    connection_string = (
                        f"mongodb://{self.mongodb_config['username']}:"
                        f"{self.mongodb_config['password']}@"
                        f"{self.mongodb_config['host']}:{self.mongodb_config['port']}"
                    )
                else:
                    connection_string = (
                        f"mongodb://{self.mongodb_config['host']}:"
                        f"{self.mongodb_config['port']}"
                    )
                
                self._mongodb_client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000,
                    maxPoolSize=10
                )
                
                # Test connection
                self._mongodb_client.admin.command('ping')
                logger.info("Connected to MongoDB successfully")
            except Exception as e:
                logger.error(f"MongoDB connection error: {e}")
                self._mongodb_client = None
                raise
        return self._mongodb_client
    
    def get_mongodb_database(self):
        """Get MongoDB database"""
        client = self.get_mongodb_client()
        return client[self.mongodb_config['database']]
    
    def get_redis_client(self) -> redis.Redis:
        """Get Redis client (singleton pattern)"""
        if self._redis_client is None:
            try:
                # Filter out None password
                config = {k: v for k, v in self.redis_config.items() if v is not None}
                self._redis_client = redis.Redis(**config)
                
                # Test connection
                self._redis_client.ping()
                logger.info("Connected to Redis successfully")
            except Exception as e:
                logger.error(f"Redis connection error: {e}")
                self._redis_client = None
                raise
        return self._redis_client
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections"""
        results = {}
        
        # Test PostgreSQL
        try:
            with self.get_postgres_cursor() as cursor:
                cursor.execute("SELECT 1")
                results['postgresql'] = True
            logger.info("PostgreSQL connection test: SUCCESS")
        except Exception as e:
            logger.error(f"PostgreSQL connection test: FAILED - {e}")
            results['postgresql'] = False
        
        # Test MongoDB
        try:
            client = self.get_mongodb_client()
            client.admin.command('ping')
            results['mongodb'] = True
            logger.info("MongoDB connection test: SUCCESS")
        except Exception as e:
            logger.error(f"MongoDB connection test: FAILED - {e}")
            results['mongodb'] = False
        
        # Test Redis
        try:
            redis_client = self.get_redis_client()
            redis_client.ping()
            results['redis'] = True
            logger.info("Redis connection test: SUCCESS")
        except Exception as e:
            logger.error(f"Redis connection test: FAILED - {e}")
            results['redis'] = False
        
        return results
    
    def close_connections(self):
        """Close all database connections"""
        if self._mongodb_client:
            try:
                self._mongodb_client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")
            finally:
                self._mongodb_client = None
        
        if self._redis_client:
            try:
                self._redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._redis_client = None


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for direct access
def get_postgres_connection():
    """Get PostgreSQL connection"""
    return db_manager.get_postgres_connection()

def get_postgres_cursor():
    """Get PostgreSQL cursor"""
    return db_manager.get_postgres_cursor()

def get_mongodb():
    """Get MongoDB database"""
    return db_manager.get_mongodb_database()

def get_redis():
    """Get Redis client"""
    return db_manager.get_redis_client()

def execute_query(query: str, params: tuple = None, fetch: bool = False):
    """Execute a query with JSON support"""
    return db_manager.execute_query(query, params, fetch)

def prepare_json_data(data: Any):
    """Prepare data for PostgreSQL insertion"""
    return db_manager.prepare_json_data(data)

def test_all_connections():
    """Test all database connections"""
    return db_manager.test_connections()


# Example usage functions
def create_user_example(username: str, email: str, password_hash: str, 
                       metadata: dict = None, preferences: dict = None) -> Optional[int]:
    """
    Example function showing how to create a user with JSON data
    """
    user_data = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'metadata': metadata or {},
        'preferences': preferences or {}
    }
    
    try:
        return db_manager.insert_user(user_data)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise


# Initialize logging if not already done
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )