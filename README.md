# DocTrace

> **Deterministic Documentation Verification Engine**

DocTrace is an evidence-first documentation verification system designed to ensure that technical documentation never drifts from codebase reality. 

## Architectural Principle
> **The LLM never decides whether documentation is correct.** 
> The LLM extracts claims and explains deterministic verification results; the deterministic code verification engine remains the sole source of truth.

## Monorepo Structure
- `backend/`: FastAPI Python 3.12 backend (Hexagonal Architecture / Ports & Adapters)
- `frontend/`: React 19, TypeScript, and Tailwind CSS developer dashboard shell

## Local Development Setup
See individual `backend/README.md` and `frontend/README.md` instructions for setting up environments using `uv` and `npm`.

## Workflow

```text
Requirement document
        -> extracted claims (LLM, via Groq)
        -> GitHub repository fetch (public repos, main/master branch)
        -> real AST parsing of the fetched Python source
        -> deterministic, explainable claim <-> code matching
        -> persisted traceability links + verification status
        -> compliance / coverage metrics
```

Nothing above is faked: if the LLM provider isn't configured or fails, or a
GitHub repository can't be fetched, DocTrace returns a clear error instead
of fabricating claims, code, or trace links.

## Environment Variables

Copy `.env.example` to `.env` at the repo root and fill in what you need:

| Variable | Used by | Required |
| --- | --- | --- |
| `GROQ_API_KEY` | backend claim extraction (Groq via the OpenAI-compatible API) | Yes, for extraction endpoints |
| `OPENAI_API_KEY` | backend settings (reserved; not currently called) | No |
| `BACKEND_CORS_ORIGINS` | backend CORS allow-list | Recommended for local dev |
| `PROJECT_NAME`, `API_V1_STR`, `ENVIRONMENT` | backend app metadata | No, sensible defaults |

The frontend has its own `frontend/.env.example` documenting
`VITE_API_BASE_URL`.

## Testing

Backend: `cd backend && uv run pytest`. Tests mock the LLM provider and
GitHub network calls -- no API key or network access is required to run
the suite.

Frontend: `cd frontend && npm run lint && npm run build`.

## Limitations

- GitHub integration only supports public repositories on `main`/`master`
  and only parses `.py` files.
- Claim extraction depends on a configured Groq API key; there is no local
  LLM fallback.
- No authentication layer; this is a single-tenant demo application.