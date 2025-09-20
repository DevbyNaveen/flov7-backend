# Flov7 Backend

AI-powered workflow automation platform built with FastAPI microservices.

## 🎯 Overview

Flov7 is an AI-powered workflow automation platform that allows users to create complex workflows using natural language prompts. The platform implements a 5-primitives system (Trigger, Action, Connection, Condition, Data) for building flexible and powerful workflows.

## 🏗️ Architecture

This project consists of 3 main microservices:

- **API Gateway** (Port 8000): Authentication, routing, and rate limiting
- **AI Service** (Port 8001): OpenAI GPT-4 integration and workflow generation
- **Workflow Service** (Port 8002): Temporal orchestration and CrewAI execution

### 📡 Service Communication

```bash
API Gateway
├── Forward AI requests → AI Service
├── Forward workflow requests → Workflow Service
└── Handle authentication & rate limiting

AI Service
├── Generate workflows from natural language
├── Validate workflow structures
└── Return AI metadata

Workflow Service
├── Execute workflows with Temporal
├── Process with CrewAI agents
└── Track execution status

```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Setup

1. Clone the repository
2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```

3. Configure your environment variables in `.env`

4. Start the services:

   ```bash
   docker-compose -f docker/docker-compose.dev.yml up
   ```

### Manual Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies for each service:
   ```bash
   cd api-gateway && pip install -r requirements.txt
   cd ../ai-service && pip install -r requirements.txt
   cd ../workflow-service && pip install -r requirements.txt
   ```

## 📁 Project Structure

```bash
flov7-backend/
├── api-gateway/          # FastAPI Gateway Service
├── ai-service/           # OpenAI + 5-primitives Service
├── workflow-service/     # Temporal + CrewAI Service
├── shared/               # Common utilities and models
├── tests/                # Testing framework
├── docker/               # Docker configuration
├── docs/                 # Documentation
└── scripts/              # Automation scripts
```

## 🔧 Development

### Running Individual Services
```bash
# API Gateway
cd api-gateway && uvicorn app.main:app --reload --port 8000

# AI Service
cd ai-service && uvicorn app.main:app --reload --port 8001

# Workflow Service
cd workflow-service && uvicorn app.main:app --reload --port 8002
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `OPENAI_API_KEY`
- Other service-specific variables

## 🧪 Testing
```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run tests
pytest
```

## 📚 Documentation
- [API Documentation](./docs/api/)
- [Architecture](./docs/architecture/)
- [Deployment](./docs/deployment/)

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
