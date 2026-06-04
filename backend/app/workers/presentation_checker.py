from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.presentation_checker.check_presentation")
def check_presentation(submission_id: str) -> None:
    # Implemented in Step 7.
    return None
