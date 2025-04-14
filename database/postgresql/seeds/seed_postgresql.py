#!/usr/bin/env python3
"""
PostgreSQL Database Seeder for Decentralized News Application
Seeds the PostgreSQL database with demo data for development and testing
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'news_app'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)

def load_demo_data():
    """Load demo data from JSON files"""
    # Get the correct path to the seeds directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    seeds_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'seeds')
    
    data_files = {
        'users': os.path.join(seeds_dir, 'demo_users.json'),
        'articles': os.path.join(seeds_dir, 'demo_articles.json'),
        'interactions': os.path.join(seeds_dir, 'demo_interactions.json'),
        'embeddings': os.path.join(seeds_dir, 'demo_embeddings.json')
    }
    
    data = {}
    for key, filename in data_files.items():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
            print(f"Loaded {len(data[key])} {key}")
        except FileNotFoundError:
            print(f"Demo data file not found: {filename}")
            print("Please run generate_demo_data.py first to create demo data.")
            sys.exit(1)
    
    return data

def seed_users(conn, users: List[Dict[str, Any]]):
    """Seed users table"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE users CASCADE")
    
    insert_query = """
    INSERT INTO users (
        id, username, email, password_hash, role, did_address, anonymous_mode,
        created_at, updated_at, last_active, is_active, profile_data, 
        preferences, verification_status, reputation_score
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    for user in users:
        cursor.execute(insert_query, (
            user['id'],
            user['username'],
            user['email'],
            user['password_hash'],
            user['role'],
            user['did_address'],
            user['anonymous_mode'],
            user['created_at'],
            user['updated_at'],
            user['last_active'],
            user['is_active'],
            json.dumps(user['profile_data']),
            json.dumps(user['preferences']),
            user['verification_status'],
            user['reputation_score']
        ))
    
    # Insert user preferences
    cursor.execute("TRUNCATE TABLE user_preferences CASCADE")
    
    pref_insert_query = """
    INSERT INTO user_preferences (
        user_id, categories, languages, reading_time_preference,
        content_freshness_weight, diversity_preference, personalization_level,
        explicit_feedback, created_at, updated_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for user in users:
        prefs = user['preferences']
        cursor.execute(pref_insert_query, (
            user['id'],
            prefs['categories'],
            prefs['languages'],
            prefs['reading_time_preference'],
            prefs['content_freshness_weight'],
            prefs['diversity_preference'],
            prefs['personalization_level'],
            json.dumps({}),  # explicit_feedback
            user['created_at'],
            user['updated_at']
        ))
    
    conn.commit()
    print(f"Seeded {len(users)} users and preferences")

def seed_articles(conn, articles: List[Dict[str, Any]]):
    """Seed articles table"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE articles CASCADE")
    
    insert_query = """
    INSERT INTO articles (
        id, title, content, summary, author_id, anonymous_author, category,
        subcategory, tags, language, reading_time, word_count, status,
        published_at, created_at, updated_at, metadata, source_url, image_urls,
        seo_keywords, engagement_score, quality_score, trending_score,
        view_count, like_count, comment_count, share_count
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    for article in articles:
        cursor.execute(insert_query, (
            article['id'],
            article['title'],
            article['content'],
            article['summary'],
            article['author_id'],
            article['anonymous_author'],
            article['category'],
            article['subcategory'],
            article['tags'],
            article['language'],
            article['reading_time'],
            article['word_count'],
            article['status'],
            article['published_at'],
            article['created_at'],
            article['updated_at'],
            json.dumps(article['metadata']),
            article['metadata'].get('source_url'),
            article['metadata'].get('image_urls', []),
            article['metadata'].get('seo_keywords', []),
            article['engagement_score'],
            article['quality_score'],
            article['trending_score'],
            article['view_count'],
            article['like_count'],
            article['comment_count'],
            article['share_count']
        ))
    
    conn.commit()
    print(f"Seeded {len(articles)} articles")

def seed_interactions(conn, interactions: List[Dict[str, Any]]):
    """Seed user_interactions table"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE user_interactions CASCADE")
    
    insert_query = """
    INSERT INTO user_interactions (
        id, user_id, article_id, interaction_type, interaction_strength,
        reading_progress, time_spent, created_at, session_id, device_type,
        context_data
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for interaction in interactions:
        cursor.execute(insert_query, (
            interaction['id'],
            interaction['user_id'],
            interaction['article_id'],
            interaction['interaction_type'],
            interaction['interaction_strength'],
            interaction['reading_progress'],
            interaction['time_spent'],
            interaction['created_at'],
            interaction['session_id'],
            interaction['device_type'],
            json.dumps(interaction['context_data'])
        ))
    
    conn.commit()
    print(f"Seeded {len(interactions)} user interactions")

def seed_ml_embeddings(conn, embeddings: List[Dict[str, Any]]):
    """Seed ML embedding tables"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE user_embeddings CASCADE")
    cursor.execute("TRUNCATE TABLE article_embeddings CASCADE")
    
    user_embed_query = """
    INSERT INTO user_embeddings (
        id, user_id, model_type, embedding_vector, embedding_dimension,
        model_version, created_at, updated_at, is_active
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    article_embed_query = """
    INSERT INTO article_embeddings (
        id, article_id, model_type, embedding_vector, embedding_dimension,
        content_features, semantic_features, model_version, created_at,
        updated_at, is_active
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    user_embeddings = [e for e in embeddings if e['entity_type'] == 'user']
    article_embeddings = [e for e in embeddings if e['entity_type'] == 'article']
    
    for embedding in user_embeddings:
        cursor.execute(user_embed_query, (
            embedding['id'],
            embedding['entity_id'],
            embedding['model_type'],
            embedding['embedding_vector'],
            embedding['embedding_dimension'],
            embedding['model_version'],
            embedding['created_at'],
            embedding['updated_at'],
            embedding['is_active']
        ))
    
    for embedding in article_embeddings:
        cursor.execute(article_embed_query, (
            embedding['id'],
            embedding['entity_id'],
            embedding['model_type'],
            embedding['embedding_vector'],
            embedding['embedding_dimension'],
            json.dumps({}),  # content_features
            json.dumps({}),  # semantic_features
            embedding['model_version'],
            embedding['created_at'],
            embedding['updated_at'],
            embedding['is_active']
        ))
    
    conn.commit()
    print(f"Seeded {len(user_embeddings)} user embeddings and {len(article_embeddings)} article embeddings")

def create_sample_recommendations(conn, users: List[Dict[str, Any]], articles: List[Dict[str, Any]]):
    """Create sample recommendation cache entries"""
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE recommendation_cache CASCADE")
    
    insert_query = """
    INSERT INTO recommendation_cache (
        id, user_id, recommended_articles, recommendation_scores,
        recommendation_reasons, model_ensemble, cache_timestamp,
        expiry_timestamp, impression_count, click_through_rate, is_active
    ) VALUES (%s, %s, %s::uuid[], %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    import uuid
    from datetime import datetime, timedelta
    import random
    
    # Create recommendations for first 100 users
    for user in users[:100]:
        # Select random articles for recommendation
        recommended_article_ids = [a['id'] for a in random.sample(articles, min(20, len(articles)))]
        scores = [round(random.uniform(0.1, 0.95), 4) for _ in recommended_article_ids]
        scores.sort(reverse=True)  # Sort scores in descending order
        
        reasons = {str(i): f"Based on {random.choice(['reading history', 'similar users', 'content similarity', 'trending'])}" 
                  for i, _ in enumerate(recommended_article_ids)}
        
        cursor.execute(insert_query, (
            str(uuid.uuid4()),
            user['id'],
            recommended_article_ids,  # Keep as strings, PostgreSQL will cast to UUID[]
            scores,
            json.dumps(reasons),
            "two_tower+cnn+diversity_rerank",
            datetime.now(),
            datetime.now() + timedelta(hours=24),
            random.randint(0, 5),
            round(random.uniform(0.02, 0.15), 4),
            True
        ))
    
    conn.commit()
    print("Created sample recommendation cache entries")

def main():
    """Main seeding function"""
    print("Starting PostgreSQL database seeding...")
    
    # Load demo data
    data = load_demo_data()
    
    # Connect to database
    conn = connect_db()
    
    try:
        # Seed data in order (respecting foreign key constraints)
        seed_users(conn, data['users'])
        seed_articles(conn, data['articles'])
        seed_interactions(conn, data['interactions'])
        seed_ml_embeddings(conn, data['embeddings'])
        create_sample_recommendations(conn, data['users'], data['articles'])
        
        print("\nPostgreSQL database seeding completed successfully!")
        print(f"Database: {DB_CONFIG['database']} at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during seeding: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()