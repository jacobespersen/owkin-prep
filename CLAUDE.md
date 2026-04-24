# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agentic web app for querying gene/cancer expression data via natural language chat. A FastAPI backend serves a single-page HTML frontend and a `/chat` endpoint that runs an agent loop: user messages + tool definitions are sent to Claude (Haiku), tool calls are executed locally against a CSV-backed data layer, and the final text response is returned.

Single Docker container. No database, no server-side sessions. Conversation state lives in the browser.

## Philosophy

- **Consider conventions before implementing** — before writing code, think about established conventions for file organisation, directory structure, and separation of concerns. CSS belongs in `app/static/css/`, JS in `app/static/js/`, etc. Don't default to the quickest approach if a better one is standard practice.
- **Consistent patterns** — follow the patterns already established in the codebase. When in doubt, look at how similar things are already done.
- **Packages before custom code** — before writing custom implementations for common problems, search for well-maintained packages that solve the problem. Only write custom code when no suitable package exists.
- **Ask, don't assume** — if instructions are ambiguous or incomplete, ask for clarification before proceeding.

## Architecture

```
Browser (vanilla HTML/JS/CSS — no build step)
  └─ POST /chat { api_key, messages }
       ▼
FastAPI Backend (single process)
  ├── app/main.py    — FastAPI app, /chat agent loop, serves static files
  ├── app/data.py    — loads owkin_take_home_data.csv into pandas, exposes get_targets/get_expressions/get_available_cancers
  ├── app/tools.py   — Anthropic tool schemas, execute_tool dispatcher, build_system_prompt
  └── app/static/index.html — chat UI (inline CSS/JS)
```

- **API key from frontend**: Sent per request, never stored server-side. No env vars needed.
- **Full conversation history per request**: Backend is stateless.
- **Model**: `claude-haiku-4-5-20251001`
- **No streaming**: Synchronous request/response for simplicity.

## Data

`owkin_take_home_data.csv` — columns: `cancer_indication`, `gene`, `median_value`. 10 cancer types, ~80 gene entries. Loaded once at import time by `app/data.py`.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run a single test file
pytest tests/test_data.py -v

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker
docker compose up --build
```

## Conventions

- **Python 3.11+**
- **Pydantic request/response models** — define explicit Pydantic schemas for API input and output. Don't return raw dicts from endpoints.
- **Tools use Anthropic tool-use schemas** — not OpenAI function calling format.
- **Endpoint handlers should be thin** — extract multi-step logic into service functions or the data/tools layers rather than letting route handlers balloon.
- **Keep README current** — when adding or changing setup steps, architecture, or project structure, update README.md as part of the same change.

## Testing

- **Test-driven development** — write tests before implementation when possible.
- **Test file organization** — mirrors source structure under `tests/`.
- Tests use `pytest` with `httpx` for endpoint testing.

## Deployment

- Docker image pushed to `ghcr.io/jacobespersen/owkin-agent` via GitHub Actions on push to main (`.github/workflows/deploy.yml`)
- Kubernetes manifests in `k8s/` (Deployment + Service)
- Exposed via Cloudflare tunnel at `owkin.jacobespersen.com`

## Key Design Decisions

- The agent loop in `/chat` has a max of 10 iterations to prevent runaway tool calls
- `get_expressions` returns median values across all cancer types for the given genes (not filtered by cancer) — this is by design per the CSV structure
- The system prompt dynamically includes available cancer types from the data

## Implementation Plans

When creating implementation plans (via plan mode or otherwise), save them to `docs/superpowers/plans/` with a date prefix and descriptive slug (e.g., `2026-04-24-gene-cancer-agent.md`).


