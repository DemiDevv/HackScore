from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.doc_validator.validate_documentation")
def validate_documentation(submission_id: str) -> None:
    # Implemented in Step 6.
    return None
