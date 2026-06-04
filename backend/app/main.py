from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.criteria import router as criteria_router
from app.api.hackathons import router as hackathons_router
from app.api.scoring import router as scoring_router
from app.api.submissions import router as submissions_router
from app.api.teams import router as teams_router
from app.config import settings


app = FastAPI(
    title="HackScore API",
    description="API for automated hackathon submission checks and expert scoring.",
    version="0.1.0",
    docs_url=f"{settings.api_prefix}/docs",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.api_prefix}/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(hackathons_router, prefix=settings.api_prefix)
app.include_router(teams_router, prefix=settings.api_prefix)
app.include_router(criteria_router, prefix=settings.api_prefix)
app.include_router(submissions_router, prefix=settings.api_prefix)
app.include_router(scoring_router, prefix=settings.api_prefix)
