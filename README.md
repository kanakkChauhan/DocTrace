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