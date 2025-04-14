// MongoDB Schema Definitions for Decentralized News Application
// These schemas define the structure and validation rules for MongoDB collections

// Database initialization - authenticate first
db = db.getSiblingDB('admin');
db.auth('admin', 'password');

// Switch to application database
db = db.getSiblingDB('news_app');

// Users collection schema with validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "password_hash", "role"],
      properties: {
        _id: { bsonType: "objectId" },
        username: { 
          bsonType: "string", 
          minLength: 3,
          maxLength: 50,
          pattern: "^[a-zA-Z0-9_]+$"
        },
        email: { 
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        password_hash: { bsonType: "string" },
        role: { 
          bsonType: "string", 
          enum: ["author", "reader", "administrator", "auditor"] 
        },
        did_address: { bsonType: ["string", "null"] },
        anonymous_mode: { bsonType: "bool" },
        profile_data: {
          bsonType: "object",
          properties: {
            first_name: { bsonType: ["string", "null"] },
            last_name: { bsonType: ["string", "null"] },
            bio: { bsonType: ["string", "null"] },
            avatar_url: { bsonType: ["string", "null"] },
            location: { bsonType: ["string", "null"] },
            website: { bsonType: ["string", "null"] },
            social_links: { bsonType: ["object", "null"] }
          }
        },
        preferences: {
          bsonType: "object",
          properties: {
            categories: { 
              bsonType: "array", 
              items: { bsonType: "string" } 
            },
            languages: { 
              bsonType: "array", 
              items: { bsonType: "string" } 
            },
            reading_time_preference: { bsonType: "int" },
            content_freshness_weight: { bsonType: "double" },
            diversity_preference: { bsonType: "double" },
            personalization_level: { bsonType: "double" },
            notification_settings: { bsonType: "object" },
            theme: { bsonType: "string", enum: ["light", "dark", "auto"] }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        last_active: { bsonType: "date" },
        is_active: { bsonType: "bool" },
        verification_status: { bsonType: "bool" },
        reputation_score: { bsonType: "double" },
        follower_count: { bsonType: "int" },
        following_count: { bsonType: "int" }
      }
    }
  }
});

// Articles collection schema
db.createCollection("articles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "content", "category", "language"],
      properties: {
        _id: { bsonType: "objectId" },
        title: { 
          bsonType: "string", 
          minLength: 5,
          maxLength: 500 
        },
        content: { 
          bsonType: "string", 
          minLength: 100 
        },
        summary: { bsonType: ["string", "null"] },
        author_id: { bsonType: ["objectId", "null"] },
        anonymous_author: { bsonType: "bool" },
        category: { bsonType: "string" },
        subcategory: { bsonType: ["string", "null"] },
        tags: { 
          bsonType: "array", 
          items: { bsonType: "string" } 
        },
        language: { bsonType: "string" },
        reading_time: { bsonType: "int" },
        word_count: { bsonType: "int" },
        status: { 
          bsonType: "string", 
          enum: ["draft", "published", "archived", "blocked"] 
        },
        published_at: { bsonType: ["date", "null"] },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        metadata: {
          bsonType: "object",
          properties: {
            source_url: { bsonType: ["string", "null"] },
            image_urls: { 
              bsonType: "array", 
              items: { bsonType: "string" } 
            },
            seo_keywords: { 
              bsonType: "array", 
              items: { bsonType: "string" } 
            },
            external_id: { bsonType: ["string", "null"] },
            crawled_at: { bsonType: ["date", "null"] }
          }
        },
        engagement_metrics: {
          bsonType: "object",
          properties: {
            view_count: { bsonType: "long" },
            like_count: { bsonType: "int" },
            comment_count: { bsonType: "int" },
            share_count: { bsonType: "int" },
            save_count: { bsonType: "int" },
            engagement_score: { bsonType: "double" },
            quality_score: { bsonType: "double" },
            trending_score: { bsonType: "double" }
          }
        },
        content_analysis: {
          bsonType: "object",
          properties: {
            sentiment_score: { bsonType: "double" },
            readability_score: { bsonType: "double" },
            topics: { 
              bsonType: "array", 
              items: { 
                bsonType: "object",
                properties: {
                  name: { bsonType: "string" },
                  confidence: { bsonType: "double" }
                }
              }
            },
            entities: { 
              bsonType: "array", 
              items: {
                bsonType: "object",
                properties: {
                  text: { bsonType: "string" },
                  type: { bsonType: "string" },
                  confidence: { bsonType: "double" }
                }
              }
            }
          }
        }
      }
    }
  }
});

// User interactions collection
db.createCollection("user_interactions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "article_id", "interaction_type"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        article_id: { bsonType: "objectId" },
        interaction_type: { 
          bsonType: "string", 
          enum: ["like", "dislike", "save", "share", "view", "comment"] 
        },
        interaction_strength: { bsonType: "double" },
        reading_progress: { bsonType: "double" },
        time_spent: { bsonType: "int" },
        created_at: { bsonType: "date" },
        session_id: { bsonType: ["string", "null"] },
        device_type: { bsonType: "string" },
        context_data: {
          bsonType: "object",
          properties: {
            referrer: { bsonType: ["string", "null"] },
            scroll_depth: { bsonType: ["double", "null"] },
            clicks_count: { bsonType: ["int", "null"] },
            time_of_day: { bsonType: ["string", "null"] },
            day_of_week: { bsonType: ["string", "null"] }
          }
        }
      }
    }
  }
});

// ML embeddings collection for users and articles
db.createCollection("ml_embeddings", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["entity_id", "entity_type", "model_type", "embedding_vector"],
      properties: {
        _id: { bsonType: "objectId" },
        entity_id: { bsonType: "objectId" },
        entity_type: { bsonType: "string", enum: ["user", "article"] },
        model_type: { 
          bsonType: "string", 
          enum: ["two_tower", "cnn", "rnn", "gnn", "attention", "hybrid"] 
        },
        embedding_vector: { 
          bsonType: "array", 
          items: { bsonType: "double" } 
        },
        embedding_dimension: { bsonType: "int" },
        model_version: { bsonType: "string" },
        features: {
          bsonType: "object",
          properties: {
            text_features: { bsonType: ["array", "null"] },
            behavioral_features: { bsonType: ["array", "null"] },
            contextual_features: { bsonType: ["array", "null"] },
            graph_features: { bsonType: ["object", "null"] }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        is_active: { bsonType: "bool" }
      }
    }
  }
});

// Recommendation results cache
db.createCollection("recommendations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "recommended_articles", "model_ensemble"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        recommended_articles: { 
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              article_id: { bsonType: "objectId" },
              score: { bsonType: "double" },
              rank: { bsonType: "int" },
              reason: { bsonType: "string" }
            }
          }
        },
        model_ensemble: { bsonType: "string" },
        generation_context: {
          bsonType: "object",
          properties: {
            user_context: { bsonType: "object" },
            content_pool_size: { bsonType: "int" },
            diversity_applied: { bsonType: "bool" },
            personalization_weight: { bsonType: "double" }
          }
        },
        performance_metrics: {
          bsonType: "object",
          properties: {
            generation_time_ms: { bsonType: "int" },
            impression_count: { bsonType: "int" },
            click_through_rate: { bsonType: "double" },
            engagement_rate: { bsonType: "double" }
          }
        },
        created_at: { bsonType: "date" },
        expires_at: { bsonType: "date" },
        is_active: { bsonType: "bool" }
      }
    }
  }
});

// Comments collection
db.createCollection("comments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["article_id", "user_id", "content"],
      properties: {
        _id: { bsonType: "objectId" },
        article_id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        parent_comment_id: { bsonType: ["objectId", "null"] },
        content: { 
          bsonType: "string", 
          minLength: 1,
          maxLength: 2000 
        },
        is_anonymous: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        like_count: { bsonType: "int" },
        is_deleted: { bsonType: "bool" },
        moderation_status: { 
          bsonType: "string", 
          enum: ["pending", "approved", "rejected", "flagged"] 
        }
      }
    }
  }
});

// DID identities collection
db.createCollection("did_identities", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "did_address", "public_key"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        did_address: { bsonType: "string" },
        public_key: { bsonType: "string" },
        private_key_encrypted: { bsonType: ["string", "null"] },
        blockchain_network: { bsonType: "string" },
        verification_signature: { bsonType: ["string", "null"] },
        created_at: { bsonType: "date" },
        is_active: { bsonType: "bool" }
      }
    }
  }
});

// NFT author payments collection
db.createCollection("author_payments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["author_id", "article_id", "nft_token_id", "amount"],
      properties: {
        _id: { bsonType: "objectId" },
        author_id: { bsonType: "objectId" },
        article_id: { bsonType: "objectId" },
        nft_token_id: { bsonType: "string" },
        contract_address: { bsonType: "string" },
        amount: { bsonType: "decimal" },
        currency: { bsonType: "string" },
        transaction_hash: { bsonType: "string" },
        payment_status: { 
          bsonType: "string", 
          enum: ["pending", "confirmed", "failed", "cancelled"] 
        },
        created_at: { bsonType: "date" },
        confirmed_at: { bsonType: ["date", "null"] }
      }
    }
  }
});

// Model performance tracking
db.createCollection("model_performance", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["model_type", "model_version", "metrics"],
      properties: {
        _id: { bsonType: "objectId" },
        model_type: { 
          bsonType: "string", 
          enum: ["two_tower", "cnn", "rnn", "gnn", "attention", "hybrid"] 
        },
        model_version: { bsonType: "string" },
        training_date: { bsonType: "date" },
        metrics: {
          bsonType: "object",
          properties: {
            precision_at_k: { bsonType: "object" },
            recall_at_k: { bsonType: "object" },
            ndcg_at_k: { bsonType: "object" },
            auc: { bsonType: "double" },
            diversity_score: { bsonType: "double" },
            coverage: { bsonType: "double" }
          }
        },
        hyperparameters: { bsonType: "object" },
        dataset_info: {
          bsonType: "object",
          properties: {
            training_size: { bsonType: "int" },
            validation_size: { bsonType: "int" },
            test_size: { bsonType: "int" },
            data_split_strategy: { bsonType: "string" }
          }
        },
        is_production_ready: { bsonType: "bool" },
        deployment_status: { bsonType: "string" }
      }
    }
  }
});

// Create indexes for performance optimization
// Users indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "did_address": 1 }, { unique: true, sparse: true });
db.users.createIndex({ "role": 1 });
db.users.createIndex({ "is_active": 1, "last_active": -1 });

// Articles indexes
db.articles.createIndex({ "author_id": 1 });
db.articles.createIndex({ "category": 1, "subcategory": 1 });
db.articles.createIndex({ "status": 1 });
db.articles.createIndex({ "published_at": -1 });
db.articles.createIndex({ "engagement_metrics.engagement_score": -1 });
db.articles.createIndex({ "engagement_metrics.trending_score": -1 });
db.articles.createIndex({ "tags": 1 });
db.articles.createIndex({ "language": 1 });
db.articles.createIndex({ 
  "title": "text", 
  "content": "text", 
  "summary": "text" 
}, { 
  weights: { 
    "title": 10, 
    "summary": 5, 
    "content": 1 
  } 
});

// User interactions indexes
db.user_interactions.createIndex({ "user_id": 1, "created_at": -1 });
db.user_interactions.createIndex({ "article_id": 1, "interaction_type": 1 });
db.user_interactions.createIndex({ "user_id": 1, "article_id": 1, "interaction_type": 1 });
db.user_interactions.createIndex({ "session_id": 1 });

// ML embeddings indexes
db.ml_embeddings.createIndex({ "entity_id": 1, "entity_type": 1, "model_type": 1 });
db.ml_embeddings.createIndex({ "model_type": 1, "model_version": 1 });
db.ml_embeddings.createIndex({ "is_active": 1, "updated_at": -1 });

// Recommendations indexes
db.recommendations.createIndex({ "user_id": 1, "is_active": 1, "expires_at": 1 });
db.recommendations.createIndex({ "created_at": -1 });
db.recommendations.createIndex({ "model_ensemble": 1 });

// Comments indexes
db.comments.createIndex({ "article_id": 1, "created_at": -1 });
db.comments.createIndex({ "user_id": 1 });
db.comments.createIndex({ "parent_comment_id": 1 });

// DID identities indexes
db.did_identities.createIndex({ "user_id": 1 });
db.did_identities.createIndex({ "did_address": 1 }, { unique: true });

// Author payments indexes
db.author_payments.createIndex({ "author_id": 1 });
db.author_payments.createIndex({ "article_id": 1 });
db.author_payments.createIndex({ "transaction_hash": 1 }, { unique: true });

// Model performance indexes
db.model_performance.createIndex({ "model_type": 1, "model_version": 1 });
db.model_performance.createIndex({ "is_production_ready": 1, "training_date": -1 });

print("MongoDB collections and indexes created successfully!");