# Book Pilots

Docker-first foundation for a book recommendation and book club application.

## Stack

- React, TypeScript, Vite, and Vitest
- FastAPI, SQLAlchemy, asyncpg, PostgreSQL, and pytest
- JWT-ready authentication dependencies and WebSocket support
- Docker Compose and GitHub Actions

## Run locally

Optionally copy `.env.example` to `.env` and change the development values, then run:

```sh
docker compose up --build
```

Open the web app at <http://localhost:5173>. The API documentation is at
<http://localhost:8000/docs>, and the database-backed health endpoint is at
<http://localhost:8000/health>.

Stop the stack with `docker compose down`. Add `--volumes` to also remove the
local PostgreSQL data volume.

## Validate without Compose

Backend checks require Python 3.9 or newer:

```sh
cd backend
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/mypy app tests
.venv/bin/pytest
```

Frontend checks require Node.js 22:

```sh
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```