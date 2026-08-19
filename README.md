# Book Pilots

Full-stack foundation for a book recommendation and book club application. The current milestone contains infrastructure, health verification, and CI only; recommendation, club, chat, calendar, and meeting features are intentionally deferred.

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The health endpoint executes `SELECT 1` through SQLAlchemy, so a successful response verifies both FastAPI and PostgreSQL.

## Authentication

The API exposes `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, and the protected `GET /auth/me` route. Passwords use Argon2 hashing, and JWT access and refresh tokens carry distinct token types and expiration windows. The frontend stores the token pair locally, restores the current user on reload, refreshes expired access tokens, and removes both tokens on logout.

Authenticated pages are available at `/dashboard` and `/profile`; anonymous visitors are redirected to `/login`.

## Books and recommendation data

Authenticated users can search Open Library by keyword, title, author, or ISBN at `/discover`. Search documents are normalized into the internal book shape with explicit fallbacks for absent authors, covers, descriptions, publication years, ISBNs, genres, and ratings.

Saving a reading status creates or updates a PostgreSQL `books` record and a unique user/book history record. `WANT_TO_READ`, `READING`, and `READ` states, personal ratings, reviews, normalized Open Library metadata, and favorite genre preferences are retained for the future recommender. The library, details, and preferences experiences are available at `/library`, `/books/:workId`, and `/preferences`.

## Architecture

```text
frontend/  React, TypeScript, Vite, Vitest, Nginx
backend/   FastAPI, async SQLAlchemy, PostgreSQL, pytest
```

Backend code is separated into authentication, database, models, schemas, routers, services, repositories, recommender, calendar, and meeting packages. Frontend code is separated into API, components, pages, features, hooks, context, routes, and shared types.

## Local checks

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/mypy app
.venv/bin/pytest
```

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```