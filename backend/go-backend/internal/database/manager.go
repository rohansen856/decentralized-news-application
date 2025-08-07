package database

import (
	"fmt"
	"log"

	"news-app-go/internal/config"
)

type Manager struct {
	Postgres *PostgresDB
	MongoDB  *MongoDB
	Redis    *RedisDB
}

func NewManager(cfg *config.Config) (*Manager, error) {
	postgres, err := NewPostgresDB(&cfg.Database)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize PostgreSQL: %w", err)
	}

	mongodb, err := NewMongoDB(&cfg.MongoDB)
	if err != nil {
		log.Printf("Warning: Failed to initialize MongoDB: %v", err)
	}

	redis, err := NewRedisDB(&cfg.Redis)
	if err != nil {
		log.Printf("Warning: Failed to initialize Redis: %v", err)
	}

	return &Manager{
		Postgres: postgres,
		MongoDB:  mongodb,
		Redis:    redis,
	}, nil
}

func (m *Manager) Close() error {
	var errors []error

	if m.Postgres != nil {
		if err := m.Postgres.Close(); err != nil {
			errors = append(errors, fmt.Errorf("failed to close PostgreSQL: %w", err))
		}
	}

	if m.MongoDB != nil {
		if err := m.MongoDB.Close(); err != nil {
			errors = append(errors, fmt.Errorf("failed to close MongoDB: %w", err))
		}
	}

	if m.Redis != nil {
		if err := m.Redis.Close(); err != nil {
			errors = append(errors, fmt.Errorf("failed to close Redis: %w", err))
		}
	}

	if len(errors) > 0 {
		return fmt.Errorf("errors closing databases: %v", errors)
	}

	return nil
}

func (m *Manager) HealthCheck() map[string]bool {
	health := make(map[string]bool)

	health["postgres"] = false
	if m.Postgres != nil {
		health["postgres"] = m.Postgres.HealthCheck() == nil
	}

	health["mongodb"] = false
	if m.MongoDB != nil {
		health["mongodb"] = m.MongoDB.HealthCheck() == nil
	}

	health["redis"] = false
	if m.Redis != nil {
		health["redis"] = m.Redis.HealthCheck() == nil
	}

	return health
}