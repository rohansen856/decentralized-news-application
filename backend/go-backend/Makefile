.PHONY: build run test clean docker-build docker-run

# Variables
APP_NAME=news-app-go
DOCKER_IMAGE=$(APP_NAME)
MAIN_PATH=./cmd/server

# Build the application
build:
	go build -o bin/$(APP_NAME) $(MAIN_PATH)

# Run the application
run:
	go run $(MAIN_PATH)

# Run with live reload (requires air: go install github.com/cosmtrek/air@latest)
dev:
	air

# Test the application
test:
	go test -v ./...

# Test with coverage
test-coverage:
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out

# Clean build artifacts
clean:
	rm -rf bin/
	go clean

# Format code
fmt:
	go fmt ./...

# Run linter (requires golangci-lint)
lint:
	golangci-lint run

# Download dependencies
deps:
	go mod download
	go mod tidy

# Build Docker image
docker-build:
	docker build -t $(DOCKER_IMAGE) .

# Run Docker container
docker-run:
	docker run -p 8080:8080 --env-file .env $(DOCKER_IMAGE)

# Run with docker-compose
docker-compose-up:
	docker-compose up --build

# Stop docker-compose
docker-compose-down:
	docker-compose down

# Database migration (placeholder)
migrate-up:
	@echo "Run database migrations here"

# Database rollback (placeholder)
migrate-down:
	@echo "Rollback database migrations here"

# Setup development environment
setup:
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Run 'make deps' to download dependencies"

# Help
help:
	@echo "Available commands:"
	@echo "  build         - Build the application"
	@echo "  run           - Run the application"
	@echo "  dev           - Run with live reload"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage"
	@echo "  clean         - Clean build artifacts"
	@echo "  fmt           - Format code"
	@echo "  lint          - Run linter"
	@echo "  deps          - Download dependencies"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  setup         - Setup development environment"