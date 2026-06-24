# AGENTS.md

## Cursor Cloud specific instructions

MyFridge is a two-service web app:

| Service | Stack | Dev command | URL |
|---------|-------|-------------|-----|
| Backend API | FastAPI + SQLAlchemy (SQLite) | `cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | http://localhost:8000 (docs at `/docs`) |
| Frontend | React 18 + Vite | `cd frontend && npm run dev` | http://localhost:5173 |

The update script (`pip install -r backend/requirements.txt`, `npm install --prefix frontend`) already installs dependencies on startup. Standard commands live in `README.md`; below are the non-obvious caveats.

### Running / gotchas
- Invoke uvicorn as `python3 -m uvicorn ...` (not bare `uvicorn`): pip installs console scripts to `~/.local/bin`, which is not on `PATH`.
- `uvicorn --reload` watches source files only, **not** installed packages. After changing/reinstalling dependencies, restart the server manually.
- CORS and SQLite defaults work out of the box; no `.env` is required for local dev. `JWT_SECRET_KEY` falls back to an insecure dev placeholder.

### Database & seeding (important)
- The SQLite DB (`backend/myfridge.db`) is gitignored and ephemeral per VM. Tables auto-create on startup, but it starts **empty**.
- Recipe/recommendation features (including the social PageRank recommender) need recipes seeded. Populate ~225 recipes from the bundled JSON with: `cd backend && python3 -m scripts.migrate_to_db` (idempotent). This is a seeding step, intentionally not in the update script.

### AI features
- AI Chef chat / recipe generation use Groq and require `GROQ_API_KEY` (free key from console.groq.com). It is optional: inventory, recipes, auth, favorites, and the PageRank recommender all work without it.

### Tests / lint
- There is no configured automated test suite or linter (no pytest/jest/vitest, no ESLint/ruff). Verify changes by running the services and exercising endpoints, or with ad-hoc scripts (note: `backend/test_*.py` is gitignored by repo convention).

### Social PageRank recommender (feature)
- `backend/app/services/pagerank.py` computes per-user influence via personalized PageRank over the `user_follows` graph (teleport biased by weighted engagement) and ranks recipes by influence-weighted engagement. Exposed under `/api/user/follow`, `/api/user/influence`, and `/api/user/recommendations/network`.
