# Flov7 — Natural Language Workflow Engine

Flov7 lets you describe a workflow in plain English and it builds it for you.

You say: *"When a new order comes in, validate the customer, charge their card, and send a confirmation email."* Flov7 turns that into a running, orchestrated workflow — no manual wiring required.

---

## How it works

Flov7 is built as three independent microservices that work together:

```
User prompt
    ↓
API Gateway (port 8000)      — auth, routing, rate limiting
    ↓
AI Service (port 8001)       — GPT-4 parses prompt into a workflow plan
    ↓
Workflow Service (port 8002) — Temporal executes it, CrewAI handles agents
```

Every workflow is made from five building blocks:

| Primitive | What it is |
|---|---|
| **Trigger** | What starts the workflow (webhook, schedule, event) |
| **Action** | A step that does something (call API, send message, write to DB) |
| **Connection** | How data flows between steps |
| **Condition** | A branch — do this if X, otherwise do Y |
| **Data** | Values passed between steps |

---

## Quick Start

```bash
git clone https://github.com/DevbyNaveen/flov7-backend
cd flov7-backend

# Copy environment config
cp .env.example .env
# Edit .env and fill in: OPENAI_API_KEY, SUPABASE_URL, etc.

# Start all services
cd docker
docker-compose up
```

Services will be available at:
- API Gateway: `http://localhost:8000`
- AI Service: `http://localhost:8001/docs`
- Workflow Service: `http://localhost:8002`

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values. Never commit `.env` to git.

Required:
```
OPENAI_API_KEY=your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
JWT_SECRET_KEY=generate-a-random-string
TEMPORAL_HOST=temporal:7233
```

---

## Project Structure

```
flov7-backend/
├── api-gateway/               # Auth, routing, rate limiting (FastAPI)
├── ai-service/
│   ├── app/ai/
│   │   ├── workflow_generator.py   # Prompt → workflow plan
│   │   └── openai_client.py        # GPT-4 integration
│   └── app/primitives/
│       └── primitives.py           # 5-primitive workflow model
├── workflow-service/
│   ├── app/temporal/
│   │   ├── workflows.py            # Temporal workflow definitions
│   │   └── activities.py           # Individual activity steps
│   └── app/crewai/
│       ├── agents.py               # CrewAI agent definitions
│       └── workflow_orchestrator.py
└── docker/
    ├── docker-compose.yml
    ├── docker-compose.prod.yml
    └── .env.example
```

---

## Requirements

- Docker and Docker Compose
- An OpenAI API key (GPT-4 access)
- A Supabase project (free tier works)
- Temporal Cloud or self-hosted Temporal server

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Workflow orchestration | Temporal |
| Agent execution | CrewAI |
| AI model | OpenAI GPT-4 |
| Database | Supabase (PostgreSQL) |
| Cache | Redis |
| Rate limiting | slowapi |
