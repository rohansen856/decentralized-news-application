"""
Shared database connection utilities for both Flask and FastAPI backends
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
import redis
from contextlib import contextmanager
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Centralized database connection management"""
    
    def __init__(self):
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'news_app'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
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
            'password': os.getenv('REDIS_PASSWORD', None),
            'decode_responses': True
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
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"PostgreSQL connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_postgres_cursor(self) -> Generator[RealDictCursor, None, None]:
        """Get PostgreSQL cursor with automatic cleanup"""
        with self.get_postgres_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"PostgreSQL cursor error: {e}")
                raise
            finally:
                cursor.close()
    
    def get_mongodb_client(self) -> MongoClient:
        """Get MongoDB client (singleton pattern)"""
        if self._mongodb_client is None:
            try:
                connection_string = f"mongodb://{self.mongodb_config['username']}:{self.mongodb_config['password']}@{self.mongodb_config['host']}:{self.mongodb_config['port']}"
                self._mongodb_client = MongoClient(connection_string)
                # Test connection
                self._mongodb_client.admin.command('ismaster')
                logger.info("Connected to MongoDB successfully")
            except Exception as e:
                logger.error(f"MongoDB connection error: {e}")
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
                raise
        return self._redis_client
    
    def close_connections(self):
        """Close all database connections"""
        if self._mongodb_client:
            self._mongodb_client.close()
            self._mongodb_client = None
            logger.info("MongoDB connection closed")
        
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None
            logger.info("Redis connection closed")


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