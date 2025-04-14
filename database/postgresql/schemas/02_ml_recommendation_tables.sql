-- ML Recommendation System Tables for PostgreSQL
-- Tables for Two-Tower model, CNN/RNN/GNN features, and recommendation caching

-- User embeddings for ML models
CREATE TABLE IF NOT EXISTS user_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_type recommendation_model NOT NULL,
    embedding_vector DECIMAL[] NOT NULL, -- Store as array of decimals
    embedding_dimension INTEGER NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, model_type, model_version)
);

-- Article embeddings for ML models
CREATE TABLE IF NOT EXISTS article_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    model_type recommendation_model NOT NULL,
    embedding_vector DECIMAL[] NOT NULL,
    embedding_dimension INTEGER NOT NULL,
    content_features JSONB DEFAULT '{}', -- CNN/RNN extracted features
    semantic_features JSONB DEFAULT '{}', -- GNN/Attention features
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(article_id, model_type, model_version)
);

-- Two-Tower model specific data
CREATE TABLE IF NOT EXISTS two_tower_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_tower_output DECIMAL[] NOT NULL, -- User tower embedding
    item_tower_output DECIMAL[] NOT NULL, -- Item tower embedding
    similarity_score DECIMAL(10,8) NOT NULL, -- Dot product similarity
    interaction_context JSONB DEFAULT '{}', -- Additional context features
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) NOT NULL
);

-- CNN features for article content analysis
CREATE TABLE IF NOT EXISTS cnn_article_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    text_cnn_features DECIMAL[] NOT NULL, -- Text CNN features
    image_cnn_features DECIMAL[] DEFAULT NULL, -- Image CNN features if available
    title_features DECIMAL[] NOT NULL, -- Title-specific CNN features
    content_structure_features JSONB DEFAULT '{}', -- Document structure features
    model_architecture VARCHAR(100) NOT NULL, -- e.g., 'TextCNN-3-layer'
    feature_dimension INTEGER NOT NULL,
    extraction_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) NOT NULL,
    UNIQUE(article_id, model_version)
);

-- RNN/LSTM features for sequential data
CREATE TABLE IF NOT EXISTS rnn_user_sequences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sequence_data JSONB NOT NULL, -- User interaction sequence
    hidden_states DECIMAL[] NOT NULL, -- RNN hidden states
    sequence_embeddings DECIMAL[] NOT NULL, -- Final sequence embedding
    sequence_length INTEGER NOT NULL,
    sequence_type VARCHAR(50) NOT NULL, -- 'reading_history', 'interaction_sequence'
    model_architecture VARCHAR(100) NOT NULL, -- 'LSTM', 'GRU', 'BiLSTM'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) NOT NULL
);

-- GNN features for graph-based recommendations
CREATE TABLE IF NOT EXISTS gnn_graph_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL, -- Can be user_id or article_id
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('user', 'article')),
    node_features DECIMAL[] NOT NULL, -- Node feature vector
    neighbor_aggregation DECIMAL[] NOT NULL, -- Aggregated neighbor features
    graph_embedding DECIMAL[] NOT NULL, -- Final graph embedding
    hop_count INTEGER NOT NULL DEFAULT 2, -- Number of hops considered
    graph_type VARCHAR(50) NOT NULL, -- 'user_item', 'content_similarity', 'social'
    model_architecture VARCHAR(100) NOT NULL, -- 'GCN', 'GraphSAGE', 'GAT'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) NOT NULL,
    UNIQUE(entity_id, entity_type, graph_type, model_version)
);

-- Attention mechanism features
CREATE TABLE IF NOT EXISTS attention_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    attention_weights DECIMAL[] NOT NULL, -- Attention weights for different content parts
    context_vector DECIMAL[] NOT NULL, -- Computed context vector
    query_vector DECIMAL[] NOT NULL, -- User query representation
    key_vectors JSONB NOT NULL, -- Article key vectors for different aspects
    value_vectors JSONB NOT NULL, -- Article value vectors
    attention_type VARCHAR(50) NOT NULL, -- 'self_attention', 'cross_attention', 'multi_head'
    num_heads INTEGER DEFAULT 8, -- For multi-head attention
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) NOT NULL
);

-- Candidate generation results
CREATE TABLE IF NOT EXISTS candidate_generation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    generation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_type recommendation_model NOT NULL,
    candidate_articles UUID[] NOT NULL, -- Array of article IDs
    candidate_scores DECIMAL[] NOT NULL, -- Corresponding scores
    generation_strategy VARCHAR(100) NOT NULL, -- 'collaborative_filtering', 'content_based', 'hybrid'
    top_k INTEGER NOT NULL DEFAULT 100, -- Number of candidates generated
    model_version VARCHAR(50) NOT NULL,
    execution_time_ms INTEGER -- Generation time in milliseconds
);

-- Re-ranking results
CREATE TABLE IF NOT EXISTS reranking_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_candidates UUID[] NOT NULL, -- Original candidate order
    reranked_candidates UUID[] NOT NULL, -- Re-ranked candidate order
    original_scores DECIMAL[] NOT NULL,
    reranked_scores DECIMAL[] NOT NULL,
    diversity_scores DECIMAL[] NOT NULL, -- Diversity contribution of each item
    relevance_scores DECIMAL[] NOT NULL, -- Pure relevance scores
    final_scores DECIMAL[] NOT NULL, -- Combined relevance + diversity scores
    diversity_weight DECIMAL(3,2) NOT NULL DEFAULT 0.3,
    reranking_algorithm VARCHAR(100) NOT NULL, -- 'mmr', 'dpp', 'clustering_based'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) NOT NULL
);

-- Final recommendation cache
CREATE TABLE IF NOT EXISTS recommendation_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommended_articles UUID[] NOT NULL,
    recommendation_scores DECIMAL[] NOT NULL,
    recommendation_reasons JSONB DEFAULT '{}', -- Explanations for recommendations
    model_ensemble VARCHAR(200) NOT NULL, -- Combination of models used
    cache_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expiry_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    impression_count INTEGER DEFAULT 0, -- How many times shown to user
    click_through_rate DECIMAL(5,4) DEFAULT 0.0000,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, cache_timestamp)
);

-- Model training metrics and performance tracking
CREATE TABLE IF NOT EXISTS model_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_type recommendation_model NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validation_metrics JSONB NOT NULL, -- precision, recall, f1, auc, etc.
    test_metrics JSONB NOT NULL,
    hyperparameters JSONB NOT NULL,
    training_data_size INTEGER NOT NULL,
    validation_data_size INTEGER NOT NULL,
    test_data_size INTEGER NOT NULL,
    training_duration_minutes INTEGER,
    model_size_mb DECIMAL(10,2),
    inference_time_ms DECIMAL(10,4), -- Average inference time
    is_production_ready BOOLEAN DEFAULT FALSE,
    deployment_status VARCHAR(50) DEFAULT 'training',
    notes TEXT
);

-- A/B testing for recommendation models
CREATE TABLE IF NOT EXISTS recommendation_ab_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_name VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    variant VARCHAR(50) NOT NULL, -- 'control', 'variant_a', 'variant_b'
    model_configuration JSONB NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    test_start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    test_end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    conversion_events JSONB DEFAULT '{}', -- Track user actions
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(test_name, user_id)
);

-- Feature importance tracking
CREATE TABLE IF NOT EXISTS feature_importance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_type recommendation_model NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    importance_score DECIMAL(10,8) NOT NULL,
    feature_category VARCHAR(50) NOT NULL, -- 'content', 'behavioral', 'contextual', 'demographic'
    calculation_method VARCHAR(50) NOT NULL, -- 'shap', 'permutation', 'gain'
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_type, model_version, feature_name)
);

-- Indexes for ML tables
CREATE INDEX IF NOT EXISTS idx_user_embeddings_user_model ON user_embeddings(user_id, model_type);
CREATE INDEX IF NOT EXISTS idx_user_embeddings_active ON user_embeddings(is_active, updated_at);

CREATE INDEX IF NOT EXISTS idx_article_embeddings_article_model ON article_embeddings(article_id, model_type);
CREATE INDEX IF NOT EXISTS idx_article_embeddings_active ON article_embeddings(is_active, updated_at);

CREATE INDEX IF NOT EXISTS idx_two_tower_user_timestamp ON two_tower_interactions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_two_tower_similarity ON two_tower_interactions(similarity_score DESC);

CREATE INDEX IF NOT EXISTS idx_cnn_features_article ON cnn_article_features(article_id);
CREATE INDEX IF NOT EXISTS idx_cnn_features_model ON cnn_article_features(model_version, extraction_timestamp);

CREATE INDEX IF NOT EXISTS idx_rnn_sequences_user ON rnn_user_sequences(user_id, sequence_type);
CREATE INDEX IF NOT EXISTS idx_rnn_sequences_created ON rnn_user_sequences(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_gnn_entity ON gnn_graph_features(entity_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_gnn_graph_type ON gnn_graph_features(graph_type, model_version);

CREATE INDEX IF NOT EXISTS idx_attention_user_article ON attention_features(user_id, article_id);
CREATE INDEX IF NOT EXISTS idx_attention_type ON attention_features(attention_type, model_version);

CREATE INDEX IF NOT EXISTS idx_candidate_generation_user_time ON candidate_generation(user_id, generation_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_candidate_generation_model ON candidate_generation(model_type, model_version);

CREATE INDEX IF NOT EXISTS idx_reranking_user_time ON reranking_results(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reranking_algorithm ON reranking_results(reranking_algorithm, model_version);

CREATE INDEX IF NOT EXISTS idx_recommendation_cache_user_active ON recommendation_cache(user_id, is_active, expiry_timestamp);
CREATE INDEX IF NOT EXISTS idx_recommendation_cache_ctr ON recommendation_cache(click_through_rate DESC);

CREATE INDEX IF NOT EXISTS idx_model_performance_type_version ON model_performance(model_type, model_version);
CREATE INDEX IF NOT EXISTS idx_model_performance_production ON model_performance(is_production_ready, training_date DESC);

CREATE INDEX IF NOT EXISTS idx_ab_tests_test_variant ON recommendation_ab_tests(test_name, variant);
CREATE INDEX IF NOT EXISTS idx_ab_tests_user_active ON recommendation_ab_tests(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_feature_importance_model ON feature_importance(model_type, model_version);
CREATE INDEX IF NOT EXISTS idx_feature_importance_score ON feature_importance(importance_score DESC);

-- Triggers for ML tables
CREATE OR REPLACE TRIGGER update_user_embeddings_updated_at BEFORE UPDATE ON user_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_article_embeddings_updated_at BEFORE UPDATE ON article_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();