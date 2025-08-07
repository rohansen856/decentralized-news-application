package database

import (
	"context"
	"fmt"
	"time"

	"news-app-go/internal/config"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MongoDB struct {
	client   *mongo.Client
	database *mongo.Database
}

func NewMongoDB(cfg *config.MongoDBConfig) (*MongoDB, error) {
	var uri string
	if cfg.Username != "" && cfg.Password != "" {
		uri = fmt.Sprintf("mongodb://%s:%s@%s:%d", cfg.Username, cfg.Password, cfg.Host, cfg.Port)
	} else {
		uri = fmt.Sprintf("mongodb://%s:%d", cfg.Host, cfg.Port)
	}

	clientOptions := options.Client().ApplyURI(uri)
	clientOptions.SetMaxPoolSize(10)
	clientOptions.SetServerSelectionTimeout(5 * time.Second)
	clientOptions.SetConnectTimeout(5 * time.Second)

	client, err := mongo.Connect(context.TODO(), clientOptions)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := client.Ping(ctx, nil); err != nil {
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	database := client.Database(cfg.Database)

	return &MongoDB{
		client:   client,
		database: database,
	}, nil
}

func (m *MongoDB) Close() error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return m.client.Disconnect(ctx)
}

func (m *MongoDB) GetClient() *mongo.Client {
	return m.client
}

func (m *MongoDB) GetDatabase() *mongo.Database {
	return m.database
}

func (m *MongoDB) GetCollection(name string) *mongo.Collection {
	return m.database.Collection(name)
}

func (m *MongoDB) Ping() error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return m.client.Ping(ctx, nil)
}

func (m *MongoDB) HealthCheck() error {
	return m.Ping()
}