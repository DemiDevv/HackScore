from celery import Celery

from app.config import settings


celery_app = Celery(
    "hackscore",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

import app.workers.code_analyzer  # noqa: E402,F401
import app.workers.doc_validator  # noqa: E402,F401
import app.workers.presentation_checker  # noqa: E402,F401
import app.workers.video_processor  # noqa: E402,F401
