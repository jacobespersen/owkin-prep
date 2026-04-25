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
  ├── app/main.py              — FastAPI app, mounts static files, serves index.html, includes routers
  ├── app/routes/chat.py       — /chat endpoint, thin handler delegating to agent service
  ├── app/schemas/chat.py      — Pydantic request/response models (ChatRequest, ChatResponse)
  ├── app/services/agent.py    — Agent loop: calls Claude, executes tools, iterates until text response
  ├── app/services/tools.py    — Anthropic tool schemas (TOOL_DEFINITIONS), execute_tool dispatcher, build_system_prompt
  ├── app/services/data_loader.py — Loads CSV into pandas, exposes get_targets/get_expressions/get_available_cancers
  ├── app/templates/index.html — Chat UI (HTML shell)
  ├── app/static/css/style.css — Styles
  └── app/static/js/chat.js    — Frontend chat logic
```

- **API key from frontend**: Sent per request, never stored server-side. No env vars needed.
- **Full conversation history per request**: Backend is stateless.
- **Model**: `claude-haiku-4-5-20251001`
- **No streaming**: Synchronous request/response for simplicity.

## Data

`data/owkin_take_home_data.csv` — columns: `cancer_indication`, `gene`, `median_value`. 10 cancer types, ~80 gene entries. Loaded once at import time by `app/services/data_loader.py`.

## Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run linting
ruff check . && ruff format --check .

# Run type checking
mypy app

# Run security scanning
bandit -r app -ll

# Run tests
pytest -v

# Run tests with coverage
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=90

# Run a single test file
pytest tests/services/test_data_loader.py -v

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker
docker compose up --build
```

## Conventions

- **Python 3.11+**
- **Dependencies via pyproject.toml** — use `pip install -e ".[dev]"` for local development.
- **Pydantic request/response models** — define explicit Pydantic schemas in `app/schemas/`. Don't return raw dicts from endpoints.
- **Tools use Anthropic tool-use schemas** — not OpenAI function calling format.
- **Endpoint handlers should be thin** — extract multi-step logic into service functions (`app/services/`) rather than letting route handlers balloon.
- **Package structure** — routes in `app/routes/`, schemas in `app/schemas/`, business logic in `app/services/`.
- **Keep README current** — when adding or changing setup steps, architecture, or project structure, update README.md as part of the same change.

## Testing

- **Test-driven development** — write tests before implementation when possible.
- **Test file organization** — mirrors source structure under `tests/` (e.g. `tests/routes/`, `tests/schemas/`, `tests/services/`).
- Tests use `pytest` with `httpx` for endpoint testing.
- Coverage threshold is 90% (enforced in CI and `pyproject.toml`).

## CI/CD

- **CI workflow**: `.github/workflows/ci.yml` runs on push/PR to main.
  - Dockerfile linting (hadolint for `Dockerfile` and `Dockerfile.test`)
  - Ruff (lint + format check)
  - mypy type checking
  - bandit security scanning
  - pip-audit dependency scanning
  - pytest with coverage
- **Build & push**: Gated on all CI jobs passing. Pushes to `ghcr.io/jacobespersen/owkin-agent` with `latest` + timestamped tags.

## Deployment

- Docker image pushed to `ghcr.io/jacobespersen/owkin-agent` via GitHub Actions on push to main
- Kubernetes manifests in `k8s/` using Kustomize (base + production overlay)
- Exposed via Cloudflare tunnel at `owkin.jacobespersen.com`

## Key Design Decisions

- The agent loop in `app/services/agent.py` has a max of 10 iterations to prevent runaway tool calls
- `get_expressions` returns median values for given genes within a specific cancer type (filtered by `cancer_name`)
- The system prompt dynamically includes available cancer types from the data
- Unknown tool names raise `ValueError`; expected tool execution errors (`ValueError`, `KeyError`, `TypeError`) are caught and returned to Claude as error results with tracebacks logged

## Implementation Plans

When creating implementation plans (via plan mode or otherwise), save them to `docs/superpowers/plans/` with a date prefix and descriptive slug (e.g., `2026-04-24-gene-cancer-agent.md`).

