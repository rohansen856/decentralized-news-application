# Decentralized News Application

A comprehensive decentralized news platform with blockchain-based DID authentication, AI-powered recommendations, and multi-language backend support.

## 🏗️ Architecture Overview

```
pr-project-news-application/
├── backend/
│   ├── python-fastapi/          # Python backend with FastAPI
│   └── rust-actix/              # Rust backend with Actix-web
├── frontend/                    # Next.js frontend specification
├── machine-learning/
│   ├── models/                  # ML models (Two-Tower, CNN, RNN, GNN)
│   └── data-generation/         # Demo data generators
├── llm-base/                    # LLM integration for article chat
├── blockchain/
│   ├── contracts/               # Smart contracts (DID, NFT)
│   └── scripts/                 # Deployment scripts
├── database/
│   ├── schemas/                 # MongoDB schemas
│   └── demo-data/              # Sample data
├── load-balancer/              # Load balancer configuration
└── docs/                       # Documentation
```

## 🎯 Key Features

- **Multi-Role System**: Author, Reader, Administrator, Auditor roles
- **Blockchain DID**: Anonymous author identity protection
- **AI Recommendations**: Two-Tower models, CNN/RNN/GNN for personalization
- **Multi-Language Backend**: Python (FastAPI) + Rust (Actix-web)
- **LLM Integration**: Chat with articles using Ollama models
- **Smart Contracts**: DID authentication and NFT-based author payments
- **Load Balancing**: Distributed backend with rate limiting

## 🚀 Quick Start

See individual module documentation for setup instructions:
- [Backend Setup](./docs/BACKEND_SETUP.md)
- [ML Models Setup](./docs/ML_SETUP.md)
- [Blockchain Setup](./docs/BLOCKCHAIN_SETUP.md)
- [Frontend Development](./frontend/FRONTEND.md)

## 📊 Database Schema

MongoDB collections:
- `users`: User profiles and preferences
- `articles`: News articles with metadata
- `interactions`: User-article interaction data
- `recommendations`: Cached recommendation results
- `did_identities`: Blockchain DID mappings

## 🔧 Development

Choose your preferred setup method:
- **Docker**: See [Docker Setup](./docs/DOCKER_SETUP.md)
- **Local**: See [Local Setup](./docs/LOCAL_SETUP.md)