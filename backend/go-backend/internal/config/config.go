package config

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	Auth     AuthConfig
	Redis    RedisConfig
	MongoDB  MongoDBConfig
}

type ServerConfig struct {
	Port            string
	Host            string
	Environment     string
	ReadTimeout     time.Duration
	WriteTimeout    time.Duration
	ShutdownTimeout time.Duration
	MaxHeaderBytes  int
}

type DatabaseConfig struct {
	Host         string
	Port         int
	User         string
	Password     string
	DBName       string
	SSLMode      string
	MaxOpenConns int
	MaxIdleConns int
	MaxLifetime  time.Duration
}

type AuthConfig struct {
	JWTSecret          string
	JWTExpiry          time.Duration
	RefreshTokenExpiry time.Duration
	PasswordMinLength  int
}

type RedisConfig struct {
	Host        string
	Port        int
	Password    string
	DB          int
	MaxRetries  int
	PoolSize    int
	IdleTimeout time.Duration
}

type MongoDBConfig struct {
	Host     string
	Port     int
	Username string
	Password string
	Database string
}

func Load() (*Config, error) {
	if err := godotenv.Load(); err != nil && !os.IsNotExist(err) {
		return nil, fmt.Errorf("error loading .env file: %w", err)
	}

	config := &Config{
		Server: ServerConfig{
			Port:            getEnv("SERVER_PORT", "8080"),
			Host:            getEnv("SERVER_HOST", "0.0.0.0"),
			Environment:     getEnv("ENVIRONMENT", "development"),
			ReadTimeout:     getEnvDuration("SERVER_READ_TIMEOUT", 30*time.Second),
			WriteTimeout:    getEnvDuration("SERVER_WRITE_TIMEOUT", 30*time.Second),
			ShutdownTimeout: getEnvDuration("SERVER_SHUTDOWN_TIMEOUT", 30*time.Second),
			MaxHeaderBytes:  getEnvInt("SERVER_MAX_HEADER_BYTES", 1<<20), // 1 MB
		},
		Database: DatabaseConfig{
			Host:         getEnv("POSTGRES_HOST", "localhost"),
			Port:         getEnvInt("POSTGRES_PORT", 5432),
			User:         getEnv("POSTGRES_USER", "postgres"),
			Password:     getEnv("POSTGRES_PASSWORD", "password"),
			DBName:       getEnv("POSTGRES_DB", "news_app"),
			SSLMode:      getEnv("POSTGRES_SSLMODE", "disable"),
			MaxOpenConns: getEnvInt("DB_MAX_OPEN_CONNS", 100),
			MaxIdleConns: getEnvInt("DB_MAX_IDLE_CONNS", 10),
			MaxLifetime:  getEnvDuration("DB_MAX_LIFETIME", 1*time.Hour),
		},
		Auth: AuthConfig{
			JWTSecret:          getEnv("JWT_SECRET", "your-secret-key"),
			JWTExpiry:          getEnvDuration("JWT_EXPIRY", 24*time.Hour),
			RefreshTokenExpiry: getEnvDuration("REFRESH_TOKEN_EXPIRY", 7*24*time.Hour),
			PasswordMinLength:  getEnvInt("PASSWORD_MIN_LENGTH", 8),
		},
		Redis: RedisConfig{
			Host:        getEnv("REDIS_HOST", "localhost"),
			Port:        getEnvInt("REDIS_PORT", 6379),
			Password:    getEnv("REDIS_PASSWORD", ""),
			DB:          getEnvInt("REDIS_DB", 0),
			MaxRetries:  getEnvInt("REDIS_MAX_RETRIES", 3),
			PoolSize:    getEnvInt("REDIS_POOL_SIZE", 10),
			IdleTimeout: getEnvDuration("REDIS_IDLE_TIMEOUT", 5*time.Minute),
		},
		MongoDB: MongoDBConfig{
			Host:     getEnv("MONGODB_HOST", "localhost"),
			Port:     getEnvInt("MONGODB_PORT", 27017),
			Username: getEnv("MONGODB_USER", "admin"),
			Password: getEnv("MONGODB_PASSWORD", "password"),
			Database: getEnv("MONGODB_DB", "news_app"),
		},
	}

	if err := config.validate(); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return config, nil
}

func (c *Config) validate() error {
	if c.Server.Port == "" {
		return fmt.Errorf("server port is required")
	}
	if c.Database.Host == "" {
		return fmt.Errorf("database host is required")
	}
	if c.Auth.JWTSecret == "" || c.Auth.JWTSecret == "your-secret-key" {
		return fmt.Errorf("JWT secret must be set and not use default value")
	}
	return nil
}

func (c *Config) IsDevelopment() bool {
	return c.Server.Environment == "development"
}

func (c *Config) IsProduction() bool {
	return c.Server.Environment == "production"
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvDuration(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if duration, err := time.ParseDuration(value); err == nil {
			return duration
		}
	}
	return defaultValue
}