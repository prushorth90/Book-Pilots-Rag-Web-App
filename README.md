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

## Recommendation training

The backend recommendation engine combines TF-IDF cosine similarity over genres, authors, titles, and descriptions with TensorFlow/Keras user and book embeddings. Collaborative scores receive 55% weight, content similarity 35%, and normalized popularity 10%. Users with fewer than `RECOMMENDER_MIN_RATINGS` explicit ratings use a genre and content cold-start profile instead.

Training is always offline and never runs in an API request. With PostgreSQL running, create fresh artifacts with:

```bash
docker compose run --rm backend python -m app.recommender.training --epochs 20
```

This writes the TF-IDF artifact, Keras model, ID mappings, and training manifest to `backend/app/recommender/artifacts/`. Compose mounts that directory into the API container. Restart the backend after retraining so its in-memory artifact cache reloads:

```bash
docker compose restart backend
```

Authenticated clients can then request `GET /recommendations?limit=10`. Each result includes the normalized book, hybrid score, and a short explanation. If artifacts have not been trained, the endpoint returns `503` with the training instruction.

## Book clubs and roles

Authenticated users can browse clubs at `/clubs`, create clubs at `/clubs/new`, join public clubs, leave memberships, and inspect club members and reading selections. Club owners may edit or delete their club, transfer ownership, manage every role, and manage club books. Admins may edit clubs, manage members and moderators, and manage books and future meetings. Moderators are authorized for discussion and chat moderation, while all members may participate in discussions, chat, and meetings.

Backend authorization is centralized in `app/auth/club_permissions.py`. Club routes use shared editor, member-manager, book-manager, moderator, and participant checks rather than embedding role matrices in individual endpoints. Club books retain `CURRENT`, `UPCOMING`, or `COMPLETED` status in PostgreSQL; selecting a new current book moves the previous current selection to completed.

## Calendar and meetings

The authenticated `/calendar` page uses FullCalendar with month, week, and day views. Selecting a day or time range opens the scheduling panel, shows overlapping availability shared by club members, and lets club owners or admins book a meeting. Events open a detail panel with the club, organizer, attendees, local time, location or meeting link, cancellation state, and RSVP controls.

Meeting and availability timestamps require timezone-aware input and are normalized to UTC before PostgreSQL persistence. The API exposes date-range meeting queries, create/update/cancel operations, RSVP updates, personal availability replacement, and club availability queries. Browsers render returned UTC timestamps in the user’s current `Intl` timezone.

Users may also save recurring weekly rules such as Monday 6–9 PM or Saturday 10 AM–2 PM in their IANA timezone. The scheduling panel intersects invited members’ expanded weekly rules in UTC, removes slots that conflict with scheduled meetings, and offers the remaining shared openings. Invited members begin as `PENDING` and may respond `ACCEPTED`, `MAYBE`, or `DECLINED`.

Calendar filters support all joined-club meetings, meetings where the user has a non-declined attendee record, and a specific club. Upcoming events receive a distinct calendar accent and the next three non-declined meetings appear on the dashboard. Meeting creation and time changes return `409` with affected usernames when an invited member already has an overlapping scheduled meeting.

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