#!/bin/bash
# Database Setup Script for Decentralized News Application
# Sets up both PostgreSQL and MongoDB databases with schemas and demo data

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_DB=${POSTGRES_DB:-"news_app"}
POSTGRES_USER=${POSTGRES_USER:-"postgres"}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"password"}
POSTGRES_HOST=${POSTGRES_HOST:-"localhost"}
POSTGRES_PORT=${POSTGRES_PORT:-"5432"}

MONGO_DB=${MONGO_DB:-"news_app"}
MONGO_HOST=${MONGO_HOST:-"localhost"}
MONGO_PORT=${MONGO_PORT:-"27017"}
MONGO_USER=${MONGO_USER:-"admin"}
MONGO_PASSWORD=${MONGO_PASSWORD:-"password"}

echo -e "${GREEN}Starting database setup for Decentralized News Application...${NC}"

# Function to check if PostgreSQL is running
check_postgres() {
    if ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" >/dev/null 2>&1; then
        echo -e "${RED}Error: PostgreSQL is not running or not accessible at $POSTGRES_HOST:$POSTGRES_PORT${NC}"
        echo "Please start PostgreSQL and try again."
        exit 1
    fi
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
}

# Function to check if MongoDB is running
check_mongodb() {
    # First check if MongoDB is accessible
    if ! mongosh --host "$MONGO_HOST" --port "$MONGO_PORT" --eval "quit()" >/dev/null 2>&1; then
        echo -e "${RED}Error: MongoDB is not running or not accessible at $MONGO_HOST:$MONGO_PORT${NC}"
        echo "Please start MongoDB and try again."
        exit 1
    fi
    
    # Check if authentication works
    if ! mongosh --host "$MONGO_HOST" --port "$MONGO_PORT" --username "$MONGO_USER" --password "$MONGO_PASSWORD" --authenticationDatabase "admin" --eval "quit()" >/dev/null 2>&1; then
        echo -e "${YELLOW}Warning: MongoDB authentication failed, but server is running${NC}"
        echo "This might be expected for first-time setup"
    fi
    
    echo -e "${GREEN}✓ MongoDB is running${NC}"
}

# Function to setup PostgreSQL
setup_postgresql() {
    echo -e "${YELLOW}Setting up PostgreSQL...${NC}"
    
    # Create database if it doesn't exist
    PGPASSWORD="$POSTGRES_PASSWORD" createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB" 2>/dev/null || true
    
    # Run schema creation scripts
    echo "Creating PostgreSQL schemas..."
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SCRIPT_DIR/postgresql/schemas/01_core_tables.sql"
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SCRIPT_DIR/postgresql/schemas/02_ml_recommendation_tables.sql"
    
    echo -e "${GREEN}✓ PostgreSQL schemas created successfully${NC}"
}

# Function to setup MongoDB
setup_mongodb() {
    echo -e "${YELLOW}Setting up MongoDB...${NC}"
    
    # Run MongoDB schema script with authentication
    echo "Creating MongoDB collections and indexes..."
    mongosh --host "$MONGO_HOST" --port "$MONGO_PORT" --username "$MONGO_USER" --password "$MONGO_PASSWORD" --authenticationDatabase "admin" "$SCRIPT_DIR/mongodb/schemas/collections.js"
    
    echo -e "${GREEN}✓ MongoDB collections and indexes created successfully${NC}"
}

# Function to generate demo data
generate_demo_data() {
    echo -e "${YELLOW}Generating demo data...${NC}"
    
    # Activate install requirements
    pip install -r "$SCRIPT_DIR/seeds/requirements.txt" --quiet
    
    # Generate demo data
    cd "$SCRIPT_DIR/seeds"
    python generate_demo_data.py
    
    echo -e "${GREEN}✓ Demo data generated successfully${NC}"
}

# Function to seed PostgreSQL
seed_postgresql() {
    echo -e "${YELLOW}Seeding PostgreSQL with demo data...${NC}"
    
    source "$SCRIPT_DIR/seeds/venv/bin/activate"
    cd "$SCRIPT_DIR/postgresql/seeds"
    
    export POSTGRES_HOST POSTGRES_PORT POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD
    python seed_postgresql.py
    
    echo -e "${GREEN}✓ PostgreSQL seeded successfully${NC}"
}

# Function to seed MongoDB
seed_mongodb() {
    echo -e "${YELLOW}Seeding MongoDB with demo data...${NC}"
    
    source "$SCRIPT_DIR/seeds/venv/bin/activate"
    cd "$SCRIPT_DIR/mongodb/seeds"
    
    export MONGO_HOST MONGO_PORT MONGO_DB MONGO_USER MONGO_PASSWORD
    python seed_mongodb.py
    
    echo -e "${GREEN}✓ MongoDB seeded successfully${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --postgres-only     Setup only PostgreSQL"
    echo "  --mongodb-only      Setup only MongoDB"
    echo "  --schema-only       Create schemas without seeding data"
    echo "  --seed-only         Seed databases (assumes schemas exist)"
    echo "  --no-demo-data      Skip demo data generation"
    echo "  --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  POSTGRES_DB         PostgreSQL database name (default: news_app)"
    echo "  POSTGRES_USER       PostgreSQL username (default: postgres)"
    echo "  POSTGRES_PASSWORD   PostgreSQL password (default: password)"
    echo "  POSTGRES_HOST       PostgreSQL host (default: localhost)"
    echo "  POSTGRES_PORT       PostgreSQL port (default: 5432)"
    echo "  MONGO_DB            MongoDB database name (default: news_app)"
    echo "  MONGO_HOST          MongoDB host (default: localhost)"
    echo "  MONGO_PORT          MongoDB port (default: 27017)"
}

# Parse command line arguments
POSTGRES_ONLY=false
MONGODB_ONLY=false
SCHEMA_ONLY=false
SEED_ONLY=false
NO_DEMO_DATA=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --postgres-only)
            POSTGRES_ONLY=true
            shift
            ;;
        --mongodb-only)
            MONGODB_ONLY=true
            shift
            ;;
        --schema-only)
            SCHEMA_ONLY=true
            shift
            ;;
        --seed-only)
            SEED_ONLY=true
            shift
            ;;
        --no-demo-data)
            NO_DEMO_DATA=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "Configuration:"
    echo "  PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB (user: $POSTGRES_USER)"
    echo "  MongoDB: $MONGO_HOST:$MONGO_PORT/$MONGO_DB (user: $MONGO_USER)"
    echo ""
    
    # Check database connectivity
    if [ "$MONGODB_ONLY" != true ]; then
        check_postgres
    fi
    
    if [ "$POSTGRES_ONLY" != true ]; then
        check_mongodb
    fi
    
    # Setup schemas
    if [ "$SEED_ONLY" != true ]; then
        if [ "$MONGODB_ONLY" != true ]; then
            setup_postgresql
        fi
        
        if [ "$POSTGRES_ONLY" != true ]; then
            setup_mongodb
        fi
    fi
    
    # Generate and seed data
    if [ "$SCHEMA_ONLY" != true ]; then
        if [ "$NO_DEMO_DATA" != true ]; then
            generate_demo_data
            
            if [ "$MONGODB_ONLY" != true ]; then
                seed_postgresql
            fi
            
            if [ "$POSTGRES_ONLY" != true ]; then
                seed_mongodb
            fi
        fi
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Database setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start your backend services"
    echo "2. Configure your application to connect to the databases"
    echo "3. Begin testing with the generated demo data"
    echo ""
    echo "Database URLs:"
    echo "  PostgreSQL: postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
    echo "  MongoDB: mongodb://$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
}

# Run main function
main