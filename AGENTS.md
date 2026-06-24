# AGENTS.md

## Cursor Cloud specific instructions

MyFridge is a two-service app: a FastAPI backend (`backend/`) and a React + Vite frontend (`frontend/`). Standard run/build commands live in `README.md`; the notes below cover only non-obvious, durable details for this environment.

### Services

| Service  | Dir         | Dev command                                            | URL                     |
|----------|-------------|--------------------------------------------------------|-------------------------|
| Backend  | `backend/`  | `./venv/bin/uvicorn app.main:app --reload --port 8000` | http://localhost:8000   |
| Frontend | `frontend/` | `npm run dev`                                          | http://localhost:5173   |

- The backend Python deps are installed into a virtualenv at `backend/venv` (the update script creates/refreshes it). Always invoke backend tools via `./venv/bin/...` (e.g. `./venv/bin/uvicorn`, `./venv/bin/python`); there is no `pip`/`python` on PATH that targets these deps. Creating the venv requires the system package `python3-venv` (installed during environment setup).
- The frontend dev server proxies `/api` to `http://localhost:8000` (see `frontend/vite.config.js`), so the backend must be running for inventory/chat/recipe features to work. No `.env.local` is required for local dev because of this proxy.
- The backend runs out of the box with no `.env`: `DATABASE_URL` defaults to a local SQLite file (`backend/myfridge.db`, gitignored) and tables are auto-created on startup. Copy `backend/.env.example` to `backend/.env` and set `GROQ_API_KEY` only if you need the AI Chef / voice-parsing features; core inventory works without it.
- No automated test suite or linter is configured. Verify changes by building the frontend (`npm run build`) and running the services. `backend/validate_recipes.py` is a standalone data-validation script, not a unit-test suite.
- The `/fridge`, `/chef`, etc. routes are public (no login required) for local development.
