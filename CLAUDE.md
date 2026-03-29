# Chat Service — Claude Code Guide

## Project Overview

Multi-turn chat service for the Beryl platform. Runs on port `8003`.
Powered by Azure OpenAI GPT-4o with SSE streaming. Auth via auth_service introspection.

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (async)
- **LLM**: Azure OpenAI GPT-4o via `openai` SDK (AsyncAzureOpenAI)
- **ORM**: SQLAlchemy 2.x async + aiomysql
- **DB**: MySQL (`beryl` database, shared with auth_service)
- **Auth**: Calls `POST /api/v1/introspect` on auth_service to validate tokens
- **Streaming**: Server-Sent Events (SSE) via `StreamingResponse`
- **Package manager**: Poetry

## Project Layout

```
chat-service/
├── app/
│   ├── main.py            # FastAPI entry point, CORS, routers
│   ├── config.py          # pydantic-settings
│   ├── database.py        # Async SQLAlchemy engine & session
│   ├── dependencies.py    # get_current_user_id (introspect)
│   ├── models/
│   │   ├── session.py     # ChatSession ORM
│   │   └── message.py     # ChatMessage ORM
│   ├── schemas/
│   │   ├── session.py     # Session request/response schemas
│   │   └── chat.py        # Chat request schema
│   ├── services/
│   │   ├── session_service.py
│   │   └── chat_service.py   # Azure OpenAI SSE streaming
│   └── routers/
│       ├── sessions.py
│       └── chat.py
├── migrations/            # Alembic
├── pyproject.toml
├── ecosystem.config.js
├── .env.example
└── alembic.ini
```

## Key Conventions

- All DB ops are **async** (`async with get_session()`)
- Auth: every request calls auth_service introspect — no local JWT parsing
- SSE streaming: `StreamingResponse` with `text/event-stream` content type
- Session ownership enforced: users can only access their own sessions
- Azure OpenAI client is a module-level singleton (`AsyncAzureOpenAI`)

## Common Commands

```bash
poetry install
poetry run uvicorn app.main:app --reload --port 8003
poetry run alembic upgrade head
```

## Environment Variables

See `.env.example`. Minimum required:
- `DATABASE_URL`
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`
- `AUTH_SERVICE_URL`, `AUTH_SERVICE_INTROSPECT_KEY`
