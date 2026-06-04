from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.code_analyzer.analyze_code")
def analyze_code(submission_id: str) -> None:
    # Implemented in Step 5.
    return None
