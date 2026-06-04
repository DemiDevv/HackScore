from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.video_processor.process_video")
def process_video(submission_id: str) -> None:
    # Implemented in Step 8.
    return None
