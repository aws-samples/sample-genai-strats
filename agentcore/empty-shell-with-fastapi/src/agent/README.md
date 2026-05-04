# Agent

Minimal AgentCore runtime agent built with FastAPI + Uvicorn.

## Endpoints

- `POST /invocations` — echoes received headers and JSON body
- `GET /ping` — health check, returns `{"status": "healthy"}`

## Run locally

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```
