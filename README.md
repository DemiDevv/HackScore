# HackScore

HackScore is a dark dashboard application for automated hackathon submission checks, expert scoring, algorithmic tasks, and final leaderboards.

## Stack

- Frontend: React 18, Vite, TypeScript, Tailwind CSS, Zustand, Axios
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic
- Workers: Celery, Redis, code/doc/presentation/video analyzers, algorithm runner
- Database: PostgreSQL 16
- Infrastructure: Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

The backend container runs Alembic migrations on startup. Demo seed data is loaded automatically when `HACKSCORE_AUTO_SEED=true`.

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/api/health

## Demo Accounts

- `team1@hackscore.ru` / `team123` — participant
- `jury1@hackscore.ru` / `jury123` — jury
- `admin@hackscore.ru` / `admin123` — organizer

## Main Flows

- Participant: create team, upload repository/docs/presentation/screencast, submit for checks, solve algorithmic tasks.
- Jury: review submissions, inspect automatic reports, save expert scores, view leaderboard.
- Organizer: manage hackathon status, criteria, teams, algorithm tasks, and export leaderboard CSV.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed_cli
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
