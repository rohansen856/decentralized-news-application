#!/usr/bin/env python3
"""
Demo Data Generator for Decentralized News Application
Generates realistic demo data for users, articles, interactions for ML recommendation models
"""

import json
import random
import uuid
import os
import csv
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
from typing import List, Dict, Any
import hashlib

# Initialize Faker for different locales
fake = Faker(['en_US', 'en_GB', 'es_ES', 'fr_FR', 'de_DE'])

# Categories and their subcategories
NEWS_CATEGORIES = {
    'technology': ['AI', 'blockchain', 'cybersecurity', 'software', 'hardware', 'startups'],
    'politics': ['elections', 'policy', 'international', 'local', 'opinion'],
    'business': ['finance', 'markets', 'economics', 'entrepreneurship', 'corporate'],
    'science': ['research', 'medicine', 'space', 'environment', 'biology', 'physics'],
    'sports': ['football', 'basketball', 'soccer', 'olympics', 'esports'],
    'entertainment': ['movies', 'music', 'celebrities', 'tv', 'gaming'],
    'health': ['wellness', 'nutrition', 'mental_health', 'fitness', 'medical'],
    'lifestyle': ['travel', 'food', 'fashion', 'home', 'relationships']
}

LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt']

INTERACTION_TYPES = ['like', 'dislike', 'save', 'share', 'view', 'comment']

def load_sample_data():
    """Load sample data from .idea folder"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    idea_folder = os.path.join(base_dir, '.idea')
    
    sample_data = {}
    
    # Load news dataset
    news_file = os.path.join(idea_folder, 'News_Category_Dataset_v3.json')
    if os.path.exists(news_file):
        with open(news_file, 'r', encoding='utf-8') as f:
            sample_data['news_articles'] = []
            for line in f:
                try:
                    article = json.loads(line.strip())
                    sample_data['news_articles'].append(article)
                except json.JSONDecodeError:
                    continue
    
    # Load articles CSV
    articles_file = os.path.join(idea_folder, 'Articles.csv')
    if os.path.exists(articles_file):
        sample_data['articles_csv'] = []
        with open(articles_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sample_data['articles_csv'].append(row)
    
    # Load user data
    users_file = os.path.join(idea_folder, 'cached_users_1000.csv')
    if os.path.exists(users_file):
        sample_data['users_csv'] = []
        with open(users_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sample_data['users_csv'].append(row)
    
    # Load interactions data  
    interactions_file = os.path.join(idea_folder, 'cached_interactions_1000.csv')
    if os.path.exists(interactions_file):
        sample_data['interactions_csv'] = []
        with open(interactions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sample_data['interactions_csv'].append(row)
    
    return sample_data

def generate_password_hash(password: str) -> str:
    """Generate a simple hash for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_users(num_users: int = 1000) -> List[Dict[str, Any]]:
    """Generate demo users with diverse profiles"""
    users = []
    
    for i in range(num_users):
        # Determine role distribution: 70% readers, 20% authors, 8% admin, 2% auditor
        role_rand = random.random()
        if role_rand < 0.70:
            role = 'reader'
        elif role_rand < 0.90:
            role = 'author'
        elif role_rand < 0.98:
            role = 'administrator'
        else:
            role = 'auditor'
        
        # Some users prefer anonymous mode
        anonymous_mode = random.random() < 0.15
        
        user = {
            'id': str(uuid.uuid4()),
            'username': fake.user_name() + str(random.randint(1, 9999)),
            'email': fake.email(),
            'password_hash': generate_password_hash('demo123'),
            'role': role,
            'did_address': f"did:eth:0x{fake.sha256()[:40]}" if anonymous_mode else None,
            'anonymous_mode': anonymous_mode,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
            'updated_at': fake.date_time_between(start_date='-30d', end_date='now'),
            'last_active': fake.date_time_between(start_date='-7d', end_date='now'),
            'is_active': random.random() > 0.05,  # 95% active users
            'verification_status': random.random() > 0.3,  # 70% verified
            'reputation_score': round(random.uniform(0, 100), 2),
            'profile_data': {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'bio': fake.text(max_nb_chars=200) if random.random() > 0.4 else None,
                'avatar_url': f"https://api.dicebear.com/7.x/avataaars/svg?seed={fake.user_name()}",
                'location': fake.city() if random.random() > 0.3 else None,
                'website': fake.url() if random.random() > 0.7 else None,
                'social_links': {
                    'twitter': f"@{fake.user_name()}" if random.random() > 0.6 else None,
                    'linkedin': fake.url() if random.random() > 0.8 else None
                }
            },
            'preferences': {
                'categories': random.sample(list(NEWS_CATEGORIES.keys()), 
                                          k=random.randint(2, 5)),
                'languages': random.sample(LANGUAGES, k=random.randint(1, 3)),
                'reading_time_preference': random.randint(2, 15),  # minutes
                'content_freshness_weight': round(random.uniform(0.3, 1.0), 2),
                'diversity_preference': round(random.uniform(0.2, 0.8), 2),
                'personalization_level': round(random.uniform(0.5, 1.0), 2),
                'notification_settings': {
                    'email_notifications': random.random() > 0.4,
                    'push_notifications': random.random() > 0.6,
                    'recommendation_frequency': random.choice(['daily', 'weekly', 'real_time'])
                },
                'theme': random.choice(['light', 'dark', 'auto'])
            }
        }
        users.append(user)
    
    return users

def generate_articles(users: List[Dict], num_articles: int = 5000) -> List[Dict[str, Any]]:
    """Generate demo articles with realistic content"""
    articles = []
    authors = [u for u in users if u['role'] == 'author']
    
    for i in range(num_articles):
        author = random.choice(authors)
        category = random.choice(list(NEWS_CATEGORIES.keys()))
        subcategory = random.choice(NEWS_CATEGORIES[category])
        
        # Generate realistic content
        title = fake.sentence(nb_words=random.randint(6, 12))[:-1]  # Remove period
        content_paragraphs = [fake.paragraph(nb_sentences=random.randint(3, 7)) 
                            for _ in range(random.randint(5, 15))]
        content = '\n\n'.join(content_paragraphs)
        summary = fake.text(max_nb_chars=300)
        
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # ~200 words per minute
        
        # Publication status and timing
        status = random.choices(
            ['published', 'draft', 'archived'], 
            weights=[0.8, 0.15, 0.05]
        )[0]
        
        created_at = fake.date_time_between(start_date='-1y', end_date='now')
        published_at = created_at + timedelta(
            hours=random.randint(1, 48)
        ) if status == 'published' else None
        
        # Generate engagement metrics based on article age and quality
        days_since_published = (datetime.now() - (published_at or created_at)).days
        days_since_published = max(1, days_since_published)  # Avoid division by zero
        base_views = max(10, int(np.random.exponential(1000) / (days_since_published + 1)))
        
        article = {
            'id': str(uuid.uuid4()),
            'title': title,
            'content': content,
            'summary': summary,
            'author_id': author['id'] if not author['anonymous_mode'] else None,
            'anonymous_author': author['anonymous_mode'],
            'category': category,
            'subcategory': subcategory,
            'tags': random.sample(
                [fake.word() for _ in range(20)], 
                k=random.randint(3, 8)
            ),
            'language': random.choice(author['preferences']['languages']),
            'reading_time': reading_time,
            'word_count': word_count,
            'status': status,
            'published_at': published_at,
            'created_at': created_at,
            'updated_at': fake.date_time_between(start_date=created_at, end_date='now'),
            'metadata': {
                'source_url': fake.url() if random.random() > 0.7 else None,
                'image_urls': [fake.image_url() for _ in range(random.randint(0, 3))],
                'seo_keywords': random.sample(
                    [fake.word() for _ in range(15)], 
                    k=random.randint(3, 7)
                )
            },
            'view_count': base_views,
            'like_count': int(base_views * random.uniform(0.02, 0.1)),
            'comment_count': int(base_views * random.uniform(0.005, 0.03)),
            'share_count': int(base_views * random.uniform(0.01, 0.05)),
            'engagement_score': round(random.uniform(0.1, 10.0), 4),
            'quality_score': round(random.uniform(3.0, 9.5), 2),
            'trending_score': round(random.uniform(0.0, 100.0), 4)
        }
        articles.append(article)
    
    return articles

def generate_articles_from_samples(users: List[Dict], sample_articles: List[Dict], 
                                 num_articles: int = 3000) -> List[Dict[str, Any]]:
    """Generate articles using sample data as reference"""
    articles = []
    authors = [u for u in users if u['role'] == 'author']
    
    # Category mapping from sample data
    category_mapping = {
        'U.S. NEWS': 'politics',
        'POLITICS': 'politics', 
        'WORLD NEWS': 'politics',
        'BUSINESS': 'business',
        'ENTERTAINMENT': 'entertainment',
        'SPORTS': 'sports',
        'SCIENCE': 'science',
        'TECH': 'technology',
        'COMEDY': 'entertainment',
        'PARENTING': 'lifestyle',
        'STYLE & BEAUTY': 'lifestyle',
        'WELLNESS': 'health',
        'FOOD & DRINK': 'lifestyle',
        'TRAVEL': 'lifestyle'
    }
    
    for i in range(num_articles):
        # Use sample article as reference or generate new
        if i < len(sample_articles):
            sample = sample_articles[i]
            
            author = random.choice(authors)
            
            # Map category
            original_category = sample.get('category', 'ENTERTAINMENT')
            category = category_mapping.get(original_category, 'entertainment')
            subcategory = NEWS_CATEGORIES.get(category, ['general'])[0]
            
            # Use real headline and description
            title = sample.get('headline', fake.sentence(nb_words=random.randint(6, 12))[:-1])
            summary = sample.get('short_description', fake.text(max_nb_chars=300))
            
            # Generate full content based on summary
            if summary and len(summary) > 20:
                content_paragraphs = [summary]
                # Add 3-8 more paragraphs
                content_paragraphs.extend([
                    fake.paragraph(nb_sentences=random.randint(3, 6)) 
                    for _ in range(random.randint(3, 8))
                ])
            else:
                content_paragraphs = [fake.paragraph(nb_sentences=random.randint(3, 7)) 
                                    for _ in range(random.randint(5, 12))]
            
            content = '\n\n'.join(content_paragraphs)
            
            # Parse date if available
            created_at = datetime.now() - timedelta(days=random.randint(1, 365))
            if 'date' in sample and sample['date']:
                try:
                    created_at = datetime.strptime(sample['date'], '%Y-%m-%d')
                except:
                    pass
        else:
            # Generate new article when samples are exhausted
            author = random.choice(authors)
            category = random.choice(list(NEWS_CATEGORIES.keys()))
            subcategory = random.choice(NEWS_CATEGORIES[category])
            
            title = fake.sentence(nb_words=random.randint(6, 12))[:-1]
            summary = fake.text(max_nb_chars=300)
            content_paragraphs = [fake.paragraph(nb_sentences=random.randint(3, 7)) 
                                for _ in range(random.randint(5, 15))]
            content = '\n\n'.join(content_paragraphs)
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
        
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)
        
        # Publication status and timing
        status = random.choices(
            ['published', 'draft', 'archived'], 
            weights=[0.85, 0.12, 0.03]
        )[0]
        
        published_at = created_at + timedelta(
            hours=random.randint(1, 48)
        ) if status == 'published' else None
        
        # Generate engagement metrics based on article quality and age
        days_since_published = (datetime.now() - (published_at or created_at)).days
        days_since_published = max(1, days_since_published)
        base_views = max(50, int(np.random.exponential(2000) / (days_since_published + 1)))
        
        article = {
            'id': str(uuid.uuid4()),
            'title': title[:500],  # Ensure title fits in database
            'content': content,
            'summary': summary,
            'author_id': author['id'] if not author['anonymous_mode'] else None,
            'anonymous_author': author['anonymous_mode'],
            'category': category,
            'subcategory': subcategory,
            'tags': random.sample(
                [fake.word() for _ in range(20)], 
                k=random.randint(3, 8)
            ),
            'language': random.choice(author['preferences']['languages']),
            'reading_time': reading_time,
            'word_count': word_count,
            'status': status,
            'published_at': published_at,
            'created_at': created_at,
            'updated_at': fake.date_time_between(start_date=created_at, end_date='now'),
            'metadata': {
                'source_url': sample.get('link') if i < len(sample_articles) else (fake.url() if random.random() > 0.7 else None),
                'image_urls': [fake.image_url() for _ in range(random.randint(0, 2))],
                'seo_keywords': random.sample(
                    [fake.word() for _ in range(15)], 
                    k=random.randint(3, 7)
                )
            },
            'view_count': base_views,
            'like_count': int(base_views * random.uniform(0.02, 0.08)),
            'comment_count': int(base_views * random.uniform(0.005, 0.025)),
            'share_count': int(base_views * random.uniform(0.01, 0.04)),
            'engagement_score': round(random.uniform(0.5, 8.0), 4),
            'quality_score': round(random.uniform(4.0, 9.0), 2),
            'trending_score': round(random.uniform(0.0, 75.0), 4)
        }
        
        articles.append(article)
    
    return articles

def generate_user_interactions(users: List[Dict], articles: List[Dict], 
                             num_interactions: int = 50000) -> List[Dict[str, Any]]:
    """Generate realistic user-article interactions for ML training"""
    interactions = []
    
    # Filter active users and published articles
    active_users = [u for u in users if u['is_active']]
    published_articles = [a for a in articles if a['status'] == 'published']
    
    for i in range(num_interactions):
        user = random.choice(active_users)
        article = random.choice(published_articles)
        
        # User preference-based article selection bias
        user_categories = set(user['preferences']['categories'])
        if article['category'] in user_categories:
            # Higher interaction probability for preferred categories
            if random.random() < 0.3:  # Skip some non-preferred content
                continue
        
        interaction_type = random.choice(INTERACTION_TYPES)
        
        # Interaction strength based on type and user preferences
        strength_mapping = {
            'view': random.uniform(0.1, 0.3),
            'like': random.uniform(0.7, 1.0),
            'dislike': random.uniform(0.8, 1.0),
            'save': random.uniform(0.8, 1.0),
            'share': random.uniform(0.9, 1.0),
            'comment': random.uniform(0.9, 1.0)
        }
        
        interaction_strength = strength_mapping[interaction_type]
        
        # Reading progress based on interaction type
        if interaction_type == 'view':
            reading_progress = random.uniform(0.1, 1.0)
        elif interaction_type in ['like', 'save', 'comment']:
            reading_progress = random.uniform(0.6, 1.0)
        else:
            reading_progress = random.uniform(0.3, 0.9)
        
        time_spent = int(article['reading_time'] * 60 * reading_progress * random.uniform(0.5, 1.5))
        
        interaction = {
            'id': str(uuid.uuid4()),
            'user_id': user['id'],
            'article_id': article['id'],
            'interaction_type': interaction_type,
            'interaction_strength': round(interaction_strength, 2),
            'reading_progress': round(reading_progress, 2),
            'time_spent': time_spent,
            'created_at': fake.date_time_between(
                start_date=max(article['published_at'] or article['created_at'], 
                             user['created_at']),
                end_date='now'
            ),
            'session_id': str(uuid.uuid4()),
            'device_type': random.choice(['desktop', 'mobile', 'tablet']),
            'context_data': {
                'referrer': random.choice([None, 'google', 'twitter', 'facebook', 'direct']),
                'scroll_depth': round(random.uniform(0.3, 1.0), 2),
                'clicks_count': random.randint(0, 5),
                'time_of_day': random.choice(['morning', 'afternoon', 'evening', 'night']),
                'day_of_week': random.choice(['monday', 'tuesday', 'wednesday', 'thursday', 
                                           'friday', 'saturday', 'sunday'])
            }
        }
        interactions.append(interaction)
    
    return interactions

def generate_ml_embeddings(users: List[Dict], articles: List[Dict]) -> List[Dict[str, Any]]:
    """Generate sample ML embeddings for demonstration"""
    embeddings = []
    
    models = ['two_tower', 'cnn', 'rnn', 'gnn', 'attention']
    embedding_dims = {'two_tower': 128, 'cnn': 256, 'rnn': 200, 'gnn': 150, 'attention': 300}
    
    # Generate user embeddings
    for user in users[:500]:  # Limit for demo
        for model in models:
            if random.random() > 0.3:  # Not all users have all model embeddings
                continue
                
            dim = embedding_dims[model]
            embedding = np.random.normal(0, 0.1, dim).tolist()
            
            embeddings.append({
                'id': str(uuid.uuid4()),
                'entity_id': user['id'],
                'entity_type': 'user',
                'model_type': model,
                'embedding_vector': embedding,
                'embedding_dimension': dim,
                'model_version': f"{model}_v1.2",
                'created_at': fake.date_time_between(start_date='-30d', end_date='now'),
                'updated_at': fake.date_time_between(start_date='-7d', end_date='now'),
                'is_active': True
            })
    
    # Generate article embeddings
    for article in articles[:2000]:  # Limit for demo
        for model in models:
            if random.random() > 0.2:  # Most articles should have embeddings
                continue
                
            dim = embedding_dims[model]
            embedding = np.random.normal(0, 0.1, dim).tolist()
            
            embeddings.append({
                'id': str(uuid.uuid4()),
                'entity_id': article['id'],
                'entity_type': 'article',
                'model_type': model,
                'embedding_vector': embedding,
                'embedding_dimension': dim,
                'model_version': f"{model}_v1.2",
                'created_at': fake.date_time_between(start_date='-30d', end_date='now'),
                'updated_at': fake.date_time_between(start_date='-7d', end_date='now'),
                'is_active': True
            })
    
    return embeddings

def save_to_json(data: List[Dict], filename: str):
    """Save data to JSON file with proper datetime serialization"""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)

def main():
    """Generate all demo data"""
    print("Generating demo data for decentralized news application...")
    
    # Load sample data from .idea folder
    print("Loading sample data from .idea folder...")
    sample_data = load_sample_data()
    
    if sample_data.get('news_articles'):
        print(f"Found {len(sample_data['news_articles'])} sample news articles")
    if sample_data.get('users_csv'):
        print(f"Found {len(sample_data['users_csv'])} sample users")
    if sample_data.get('interactions_csv'):
        print(f"Found {len(sample_data['interactions_csv'])} sample interactions")
    
    # Generate core data
    print("Generating users...")
    users = generate_users(1000)
    
    print("Generating articles...")
    # Use sample articles if available, otherwise generate
    if sample_data.get('news_articles'):
        print("Using sample news articles as reference...")
        articles = generate_articles_from_samples(users, sample_data['news_articles'], 3000)
    else:
        articles = generate_articles(users, 5000)
    
    print("Generating user interactions...")
    interactions = generate_user_interactions(users, articles, 50000)
    
    print("Generating ML embeddings...")
    embeddings = generate_ml_embeddings(users, articles)
    
    # Save to files
    print("Saving data to files...")
    save_to_json(users, 'demo_users.json')
    save_to_json(articles, 'demo_articles.json')
    save_to_json(interactions, 'demo_interactions.json')
    save_to_json(embeddings, 'demo_embeddings.json')
    
    print(f"""
Demo data generated successfully!
- Users: {len(users)}
- Articles: {len(articles)}
- Interactions: {len(interactions)}
- ML Embeddings: {len(embeddings)}
    
Files saved:
- demo_users.json
- demo_articles.json
- demo_interactions.json
- demo_embeddings.json
    """)

if __name__ == "__main__":
    main()