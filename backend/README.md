# DocTrace Backend

FastAPI service implementing document ingestion, LLM-based claim extraction,
GitHub repository fetching, AST-based code parsing, deterministic
claim-to-code traceability matching, and compliance/coverage calculations.

## Stack

- Python 3.12, FastAPI, SQLAlchemy (SQLite by default)
- `openai` SDK pointed at Groq's OpenAI-compatible endpoint for claim
  extraction
- `requests` for GitHub repository archive fetching
- `pytest` for tests, `ruff` for linting/formatting

## Setup

```bash
uv sync
```

Copy `../.env.example` to `../.env` (project root) and fill in the values
you need. At minimum, `GROQ_API_KEY` is required for the `/documents/{id}/extract`
endpoint (and the trace endpoint's extraction fallback) to work -- without
it, those endpoints return a `503` with a clear message instead of a fake
result.

## Running

```bash
uv run uvicorn main:app --reload
```

The API is served under `/api/v1`. `GET /api/v1/system/health` is a basic
liveness check.

## Testing

```bash
uv run pytest
```

Tests never require a real LLM API key or network access to GitHub: the LLM
provider (`claim_extractor`) and `github_service` are mocked wherever a test
exercises document extraction or the GitHub trace flow.

## Linting / formatting

```bash
uv run ruff check .
uv run ruff format --check .
```

## Architecture notes

- `domain/` -- plain dataclasses (no framework dependencies).
- `infrastructure/` -- SQLAlchemy repositories and the AST parser.
- `services/` -- claim extraction, GitHub fetching, traceability scoring,
  and compliance calculation.
- `api/v1/` -- FastAPI routers; thin, delegate to services/repositories.

Claim identity is stable across requests: `/documents/{id}/extract` persists
the full claim set for a document (replacing any previous set), and
`/trace/` and `GET /trace/{id}` read that same persisted set rather than
re-extracting on every call.

## Known limitations

- GitHub fetching only supports public repositories on the `main` or
  `master` branch, and only extracts `.py` files.
- Claim extraction requires a Groq API key (`GROQ_API_KEY`); no offline/local
  LLM fallback is implemented.
- No authentication/authorization layer -- this is a single-tenant demo
  backend.