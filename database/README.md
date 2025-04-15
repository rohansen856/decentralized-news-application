# Database Setup for Decentralized News Application

This directory contains comprehensive database schemas, seed data, and setup scripts for the decentralized news application with ML-powered recommendations.

## 🗂️ Directory Structure

```
database/
├── postgresql/
│   ├── schemas/
│   │   ├── 01_core_tables.sql          # Core application tables
│   │   └── 02_ml_recommendation_tables.sql  # ML/AI recommendation tables
│   ├── seeds/
│   │   └── seed_postgresql.py          # PostgreSQL data seeding script
│   └── migrations/                     # Future database migrations
├── mongodb/
│   ├── schemas/
│   │   └── collections.js              # MongoDB collections and indexes
│   ├── seeds/
│   │   └── seed_mongodb.py             # MongoDB data seeding script
│   └── migrations/                     # Future MongoDB migrations
├── seeds/
│   ├── generate_demo_data.py           # Demo data generator
│   ├── requirements.txt                # Python dependencies
│   └── demo_*.json                     # Generated demo data files
├── redis/
│   └── redis.conf                      # Redis configuration
├── docker-compose.yml                  # Docker container orchestration
├── setup_databases.sh                  # Automated setup script
└── README.md                           # This file
```

## 🎯 Database Design Overview

### PostgreSQL (Relational Data)

**Core Tables:**
- `users` - User accounts with role-based access (author, reader, admin, auditor)
- `articles` - News articles with comprehensive metadata
- `user_interactions` - User-article interactions for ML training
- `comments` - Article comments with threading support
- `user_follows` - Social following relationships
- `did_identities` - Blockchain DID mappings for anonymous authors
- `author_payments` - NFT-based author payment tracking

**ML Recommendation Tables:**
- `user_embeddings` / `article_embeddings` - ML model embeddings storage
- `two_tower_interactions` - Two-Tower model specific data
- `cnn_article_features` - CNN-extracted content features
- `rnn_user_sequences` - Sequential user behavior data
- `gnn_graph_features` - Graph neural network features
- `attention_features` - Attention mechanism weights
- `candidate_generation` - ML candidate generation results
- `reranking_results` - Re-ranking and diversity optimization
- `recommendation_cache` - Final recommendation caching

### MongoDB (Document Storage)

**Collections:**
- `users` - Flexible user profiles and preferences
- `articles` - Rich article documents with nested metadata
- `user_interactions` - Interaction events with contextual data
- `ml_embeddings` - Unified embeddings for all ML models
- `recommendations` - Cached recommendation results
- `comments` - Threaded comments with moderation
- `did_identities` - DID blockchain mappings
- `author_payments` - Payment transaction records
- `model_performance` - ML model training metrics

## 🚀 Quick Start

### Option 1: Docker Setup (Recommended)

1. **Start databases with Docker Compose:**
   ```bash
   cd database
   docker-compose up -d
   ```

2. **Setup schemas and seed data:**
   ```bash
   ./setup_databases.sh
   ```

3. **Access services:**
   - PostgreSQL: `localhost:5432`
   - MongoDB 8.0: `localhost:27017`
   - MongoDB Latest: `localhost:27018` (with `--profile latest`)
   - Redis: `localhost:6379`
   - pgAdmin: `http://localhost:8080` (with `--profile admin`)
   - Mongo Express: `http://localhost:8081` (with `--profile admin`)

### Option 2: Local Installation

1. **Install databases locally:**
   ```bash
   # PostgreSQL 16
   sudo apt install postgresql-16 postgresql-contrib-16
   
   # MongoDB 8.0
   wget -qO - https://www.mongodb.org/static/pgp/server-8.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
   sudo apt update
   sudo apt install mongodb-org
   
   # Redis
   sudo apt install redis-server
   ```

2. **Configure and start services:**
   ```bash
   sudo systemctl start postgresql
   sudo systemctl start mongod
   sudo systemctl start redis-server
   ```

3. **Run setup script:**
   ```bash
   ./setup_databases.sh
   ```

## 🔧 Configuration

### Environment Variables

```bash
# PostgreSQL Configuration
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=news_app
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password

# MongoDB Configuration
export MONGO_HOST=localhost
export MONGO_PORT=27017
export MONGO_DB=news_app
export MONGO_USER=admin
export MONGO_PASSWORD=password

# Redis Configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=redis_password
```

### Docker Compose Profiles

- **Default**: PostgreSQL 16 + MongoDB 8.0 + Redis
- **`latest` profile**: Includes MongoDB latest version on port 27018
- **`admin` profile**: Includes pgAdmin and Mongo Express for database management

```bash
# Start with admin tools
docker-compose --profile admin up -d

# Start with MongoDB latest
docker-compose --profile latest up -d

# Start with both profiles
docker-compose --profile admin --profile latest up -d
```

## 📊 Demo Data

The setup includes comprehensive demo data generation:

- **1,000 users** with diverse profiles and preferences
- **5,000 articles** across multiple categories and languages
- **50,000 user interactions** for ML training
- **ML embeddings** for recommendation system testing
- **Comments, follows, and payment records**

### Data Generation

```bash
cd seeds
python generate_demo_data.py
```

Generated files:
- `demo_users.json` - User profiles and preferences
- `demo_articles.json` - News articles with metadata
- `demo_interactions.json` - User-article interactions
- `demo_embeddings.json` - ML model embeddings

## 🤖 ML Recommendation System

The database schema supports multiple recommendation models:

### Two-Tower Model
- User and item embeddings stored separately
- Dot-product similarity computation
- Real-time inference support

### Deep Learning Models
- **CNN**: Text and image feature extraction
- **RNN/LSTM**: Sequential user behavior modeling
- **GNN**: Graph-based collaborative filtering
- **Attention**: Multi-head attention mechanisms

### Recommendation Pipeline
1. **Candidate Generation**: Initial filtering and scoring
2. **Feature Engineering**: Multi-model feature extraction
3. **Re-ranking**: Diversity and relevance optimization
4. **Caching**: Performance-optimized result storage

## 🔒 Security Features

- **Blockchain DID Integration**: Anonymous author identity protection
- **Role-based Access Control**: Author, reader, admin, auditor roles
- **Audit Logging**: Comprehensive action tracking
- **Password Hashing**: Secure credential storage
- **NFT Payments**: Blockchain-based author compensation

## 🏗️ Advanced Setup Options

### Schema-only Setup
```bash
./setup_databases.sh --schema-only
```

### Database-specific Setup
```bash
./setup_databases.sh --postgres-only
./setup_databases.sh --mongodb-only
```

### Seed-only (assumes schemas exist)
```bash
./setup_databases.sh --seed-only
```

### Skip Demo Data Generation
```bash
./setup_databases.sh --no-demo-data
```

## 📝 Database Connections

### PostgreSQL Connection Strings
```python
# Python (psycopg2)
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="news_app",
    user="postgres",
    password="password"
)

# SQLAlchemy
DATABASE_URL = "postgresql://postgres:password@localhost:5432/news_app"
```

### MongoDB Connection Strings
```python
# PyMongo
client = MongoClient("mongodb://admin:password@localhost:27017/")
db = client.news_app

# Connection URI
MONGO_URI = "mongodb://admin:password@localhost:27017/news_app"
```

### Redis Connection
```python
# Redis-py
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    password="redis_password",
    decode_responses=True
)
```

## 🔍 Monitoring and Maintenance

### Database Health Checks
```bash
# PostgreSQL
pg_isready -h localhost -p 5432

# MongoDB
mongosh --eval "db.runCommand('ping')"

# Redis
redis-cli ping
```

### Performance Monitoring
- PostgreSQL: Use `pg_stat_statements` extension
- MongoDB: Enable profiler for slow queries
- Redis: Monitor memory usage and hit ratios

### Backup Scripts
```bash
# PostgreSQL backup
pg_dump -h localhost -U postgres news_app > backup_$(date +%Y%m%d_%H%M%S).sql

# MongoDB backup
mongodump --host localhost --db news_app --out backup_$(date +%Y%m%d_%H%M%S)/

# Redis backup
redis-cli BGSAVE
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure databases are running
2. **Permission Denied**: Check user credentials and permissions
3. **Schema Errors**: Verify SQL syntax and dependencies
4. **Demo Data Errors**: Install Python requirements first

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=1
./setup_databases.sh
```

### Reset Database
```bash
# Drop and recreate (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d
./setup_databases.sh
```

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)
- [ML Recommendation Systems](https://developers.google.com/machine-learning/recommendation)
- [Blockchain DID Specification](https://www.w3.org/TR/did-core/)

## 🤝 Contributing

1. Follow existing schema naming conventions
2. Add indexes for new query patterns
3. Update both PostgreSQL and MongoDB schemas
4. Test with generated demo data
5. Document any breaking changes

---

For questions or issues, please check the troubleshooting section or refer to the main project documentation.