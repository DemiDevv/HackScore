# HackScore

HackScore is a dark-theme web application for automated accounting and scoring of hackathon team submissions.

## Stack

- Frontend: React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui-ready structure
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic
- Infrastructure: PostgreSQL 16, Redis, Celery, Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API health check: http://localhost:8000/api/health
- Swagger docs: http://localhost:8000/api/docs

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The handoff design prototype remains in `prototype/HackScore.html`.
