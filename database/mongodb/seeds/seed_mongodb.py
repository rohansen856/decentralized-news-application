#!/usr/bin/env python3
"""
MongoDB Database Seeder for Decentralized News Application
Seeds the MongoDB database with demo data for development and testing
"""

import json
import sys
import os
from datetime import datetime, timedelta
import uuid
import random
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

# MongoDB configuration
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST', 'localhost'),
    'port': int(os.getenv('MONGO_PORT', 27017)),
    'database': os.getenv('MONGO_DB', 'news_app'),
    'username': os.getenv('MONGO_USER', 'admin'),
    'password': os.getenv('MONGO_PASSWORD', 'password')
}

def connect_mongodb():
    """Connect to MongoDB"""
    try:
        if MONGO_CONFIG['username'] and MONGO_CONFIG['password']:
            client = MongoClient(
                host=MONGO_CONFIG['host'],
                port=MONGO_CONFIG['port'],
                username=MONGO_CONFIG['username'],
                password=MONGO_CONFIG['password']
            )
        else:
            client = MongoClient(
                host=MONGO_CONFIG['host'],
                port=MONGO_CONFIG['port']
            )
        
        # Test connection
        client.admin.command('ping')
        db = client[MONGO_CONFIG['database']]
        return db
    except ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")
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
                raw_data = json.load(f)
                # Convert datetime strings back to datetime objects
                data[key] = convert_datetime_strings(raw_data)
            print(f"Loaded {len(data[key])} {key}")
        except FileNotFoundError:
            print(f"Demo data file not found: {filename}")
            print("Please run generate_demo_data.py first to create demo data.")
            sys.exit(1)
    
    return data

def convert_datetime_strings(data: List[Dict]) -> List[Dict]:
    """Convert ISO datetime strings to datetime objects"""
    datetime_fields = [
        'created_at', 'updated_at', 'last_active', 'published_at',
        'confirmed_at', 'expires_at', 'training_date'
    ]
    
    for item in data:
        for field in datetime_fields:
            if field in item and item[field]:
                try:
                    item[field] = datetime.fromisoformat(item[field].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
    
    return data

def transform_user_for_mongodb(user: Dict[str, Any]) -> Dict[str, Any]:
    """Transform user data for MongoDB schema"""
    mongo_user = {
        '_id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'password_hash': user['password_hash'],
        'role': user['role'],
        'did_address': user['did_address'],
        'anonymous_mode': user['anonymous_mode'],
        'profile_data': user['profile_data'],
        'preferences': user['preferences'],
        'created_at': user['created_at'],
        'updated_at': user['updated_at'],
        'last_active': user['last_active'],
        'is_active': user['is_active'],
        'verification_status': user['verification_status'],
        'reputation_score': user['reputation_score'],
        'follower_count': random.randint(0, 1000),
        'following_count': random.randint(0, 500)
    }
    
    return mongo_user

def transform_article_for_mongodb(article: Dict[str, Any]) -> Dict[str, Any]:
    """Transform article data for MongoDB schema"""
    mongo_article = {
        '_id': article['id'],
        'title': article['title'],
        'content': article['content'],
        'summary': article['summary'],
        'author_id': article['author_id'],
        'anonymous_author': article['anonymous_author'],
        'category': article['category'],
        'subcategory': article['subcategory'],
        'tags': article['tags'],
        'language': article['language'],
        'reading_time': article['reading_time'],
        'word_count': article['word_count'],
        'status': article['status'],
        'published_at': article['published_at'],
        'created_at': article['created_at'],
        'updated_at': article['updated_at'],
        'metadata': article['metadata'],
        'engagement_metrics': {
            'view_count': article['view_count'],
            'like_count': article['like_count'],
            'comment_count': article['comment_count'],
            'share_count': article['share_count'],
            'save_count': random.randint(0, article['like_count']),
            'engagement_score': article['engagement_score'],
            'quality_score': article['quality_score'],
            'trending_score': article['trending_score']
        },
        'content_analysis': {
            'sentiment_score': round(random.uniform(-1.0, 1.0), 3),
            'readability_score': round(random.uniform(0.3, 0.9), 3),
            'topics': [
                {
                    'name': random.choice(['politics', 'technology', 'sports', 'business']),
                    'confidence': round(random.uniform(0.6, 0.95), 3)
                }
                for _ in range(random.randint(1, 3))
            ],
            'entities': [
                {
                    'text': random.choice(['Apple', 'Google', 'Microsoft', 'Tesla', 'OpenAI']),
                    'type': 'ORGANIZATION',
                    'confidence': round(random.uniform(0.7, 0.99), 3)
                }
                for _ in range(random.randint(0, 2))
            ]
        }
    }
    
    return mongo_article

def transform_interaction_for_mongodb(interaction: Dict[str, Any]) -> Dict[str, Any]:
    """Transform interaction data for MongoDB schema"""
    mongo_interaction = {
        '_id': interaction['id'],
        'user_id': interaction['user_id'],
        'article_id': interaction['article_id'],
        'interaction_type': interaction['interaction_type'],
        'interaction_strength': interaction['interaction_strength'],
        'reading_progress': interaction['reading_progress'],
        'time_spent': interaction['time_spent'],
        'created_at': interaction['created_at'],
        'session_id': interaction['session_id'],
        'device_type': interaction['device_type'],
        'context_data': interaction['context_data']
    }
    
    return mongo_interaction

def transform_embedding_for_mongodb(embedding: Dict[str, Any]) -> Dict[str, Any]:
    """Transform embedding data for MongoDB schema"""
    mongo_embedding = {
        '_id': embedding['id'],
        'entity_id': embedding['entity_id'],
        'entity_type': embedding['entity_type'],
        'model_type': embedding['model_type'],
        'embedding_vector': embedding['embedding_vector'],
        'embedding_dimension': embedding['embedding_dimension'],
        'model_version': embedding['model_version'],
        'features': {
            'text_features': None,
            'behavioral_features': None,
            'contextual_features': None,
            'graph_features': None
        },
        'created_at': embedding['created_at'],
        'updated_at': embedding['updated_at'],
        'is_active': embedding['is_active']
    }
    
    return mongo_embedding

def seed_collection(db, collection_name: str, data: List[Dict], transform_func=None):
    """Seed a MongoDB collection with data"""
    collection = db[collection_name]
    
    # Clear existing data
    collection.delete_many({})
    print(f"Cleared existing data from {collection_name}")
    
    # Transform data if needed
    if transform_func:
        data = [transform_func(item) for item in data]
    
    # Insert data in batches
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            result = collection.insert_many(batch, ordered=False)
            total_inserted += len(result.inserted_ids)
        except DuplicateKeyError as e:
            print(f"Some duplicate keys in {collection_name}: {e}")
    
    print(f"Seeded {total_inserted} documents in {collection_name}")

def create_sample_recommendations(db, users: List[Dict], articles: List[Dict]):
    """Create sample recommendation documents"""
    recommendations = []
    
    # Create recommendations for first 100 users
    for user in users[:100]:
        recommended_articles = random.sample(articles, min(15, len(articles)))
        
        recommendation = {
            '_id': str(uuid.uuid4()),
            'user_id': user['id'],
            'recommended_articles': [
                {
                    'article_id': article['id'],
                    'score': round(random.uniform(0.1, 0.95), 4),
                    'rank': i + 1,
                    'reason': f"Based on {random.choice(['reading history', 'similar users', 'content similarity', 'trending'])}"
                }
                for i, article in enumerate(recommended_articles)
            ],
            'model_ensemble': random.choice([
                'two_tower_v1.2',
                'cnn_v1.1+diversity_rerank',
                'hybrid_ensemble_v2.0'
            ]),
            'generation_context': {
                'user_context': {
                    'recent_categories': random.sample(['technology', 'politics', 'sports'], 2),
                    'reading_time': random.randint(5, 30),
                    'device_type': random.choice(['mobile', 'desktop'])
                },
                'content_pool_size': len(articles),
                'diversity_applied': random.choice([True, False]),
                'personalization_weight': round(random.uniform(0.6, 1.0), 2)
            },
            'performance_metrics': {
                'generation_time_ms': random.randint(50, 500),
                'impression_count': random.randint(0, 10),
                'click_through_rate': round(random.uniform(0.02, 0.15), 4),
                'engagement_rate': round(random.uniform(0.05, 0.25), 4)
            },
            'created_at': datetime.now() - timedelta(hours=random.randint(1, 24)),
            'expires_at': datetime.now() + timedelta(hours=random.randint(12, 48)),
            'is_active': True
        }
        
        # Sort recommended articles by score
        recommendation['recommended_articles'].sort(key=lambda x: x['score'], reverse=True)
        recommendations.append(recommendation)
    
    seed_collection(db, 'recommendations', recommendations)

def create_sample_comments(db, users: List[Dict], articles: List[Dict]):
    """Create sample comments"""
    comments = []
    
    # Create 1000 random comments
    for _ in range(1000):
        user = random.choice(users)
        article = random.choice(articles)
        
        comment = {
            '_id': str(uuid.uuid4()),
            'article_id': article['id'],
            'user_id': user['id'],
            'parent_comment_id': None,
            'content': f"This is a sample comment about {article['title'][:50]}...",
            'is_anonymous': random.choice([True, False]),
            'created_at': datetime.now() - timedelta(days=random.randint(0, 30)),
            'updated_at': datetime.now() - timedelta(days=random.randint(0, 30)),
            'like_count': random.randint(0, 50),
            'is_deleted': False,
            'moderation_status': random.choice(['approved', 'pending', 'approved', 'approved'])  # Most approved
        }
        comments.append(comment)
    
    seed_collection(db, 'comments', comments)

def create_sample_did_identities(db, users: List[Dict]):
    """Create sample DID identities for users who want anonymous mode"""
    did_identities = []
    
    anonymous_users = [u for u in users if u['anonymous_mode']]
    
    for user in anonymous_users:
        if user['did_address']:
            did_identity = {
                '_id': str(uuid.uuid4()),
                'user_id': user['id'],
                'did_address': user['did_address'],
                'public_key': f"0x{random.randbytes(32).hex()}",
                'private_key_encrypted': f"encrypted_{random.randbytes(64).hex()}",
                'blockchain_network': 'ethereum',
                'verification_signature': f"0x{random.randbytes(65).hex()}",
                'created_at': user['created_at'],
                'is_active': True
            }
            did_identities.append(did_identity)
    
    seed_collection(db, 'did_identities', did_identities)

def create_model_performance_records(db):
    """Create sample model performance records"""
    models = ['two_tower', 'cnn', 'rnn', 'gnn', 'attention', 'hybrid']
    performance_records = []
    
    for model in models:
        for version in ['v1.0', 'v1.1', 'v1.2']:
            record = {
                '_id': str(uuid.uuid4()),
                'model_type': model,
                'model_version': version,
                'training_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'metrics': {
                    'precision_at_k': {
                        'p@5': round(random.uniform(0.6, 0.9), 3),
                        'p@10': round(random.uniform(0.5, 0.8), 3),
                        'p@20': round(random.uniform(0.4, 0.7), 3)
                    },
                    'recall_at_k': {
                        'r@5': round(random.uniform(0.3, 0.6), 3),
                        'r@10': round(random.uniform(0.4, 0.7), 3),
                        'r@20': round(random.uniform(0.5, 0.8), 3)
                    },
                    'ndcg_at_k': {
                        'ndcg@5': round(random.uniform(0.7, 0.9), 3),
                        'ndcg@10': round(random.uniform(0.65, 0.85), 3),
                        'ndcg@20': round(random.uniform(0.6, 0.8), 3)
                    },
                    'auc': round(random.uniform(0.75, 0.95), 3),
                    'diversity_score': round(random.uniform(0.3, 0.8), 3),
                    'coverage': round(random.uniform(0.6, 0.95), 3)
                },
                'hyperparameters': {
                    'learning_rate': random.choice([0.001, 0.0001, 0.0005]),
                    'batch_size': random.choice([64, 128, 256]),
                    'embedding_dim': random.choice([128, 256, 512]),
                    'dropout_rate': round(random.uniform(0.1, 0.5), 2)
                },
                'dataset_info': {
                    'training_size': random.randint(40000, 80000),
                    'validation_size': random.randint(5000, 10000),
                    'test_size': random.randint(5000, 10000),
                    'data_split_strategy': 'temporal_split'
                },
                'is_production_ready': version == 'v1.2',
                'deployment_status': 'production' if version == 'v1.2' else 'development'
            }
            performance_records.append(record)
    
    seed_collection(db, 'model_performance', performance_records)

def main():
    """Main seeding function"""
    print("Starting MongoDB database seeding...")
    
    # Load demo data
    data = load_demo_data()
    
    # Connect to MongoDB
    db = connect_mongodb()
    
    try:
        # Seed collections
        print("\nSeeding core collections...")
        seed_collection(db, 'users', data['users'], transform_user_for_mongodb)
        seed_collection(db, 'articles', data['articles'], transform_article_for_mongodb)
        seed_collection(db, 'user_interactions', data['interactions'], transform_interaction_for_mongodb)
        seed_collection(db, 'ml_embeddings', data['embeddings'], transform_embedding_for_mongodb)
        
        print("\nCreating additional collections...")
        create_sample_recommendations(db, data['users'], data['articles'])
        create_sample_comments(db, data['users'], data['articles'])
        create_sample_did_identities(db, data['users'])
        create_model_performance_records(db)
        
        print("\nMongoDB database seeding completed successfully!")
        print(f"Database: {MONGO_CONFIG['database']} at {MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}")
        
        # Print collection counts
        collections = db.list_collection_names()
        print(f"\nCollections created: {len(collections)}")
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"  {collection_name}: {count} documents")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()