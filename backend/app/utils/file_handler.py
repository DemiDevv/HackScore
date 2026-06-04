import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings


ARCHIVE_EXTENSIONS = {".zip", ".tar.gz"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".md"}
PRESENTATION_EXTENSIONS = {".pptx", ".pdf"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}

MAX_ARCHIVE_SIZE = 50 * 1024 * 1024
MAX_DEFAULT_SIZE = 20 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024

FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    cleaned = FILENAME_RE.sub("_", Path(filename).name).strip("._")
    return cleaned or f"upload-{uuid.uuid4().hex}"


def detect_extension(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".tar.gz"):
        return ".tar.gz"
    return Path(lower).suffix


def artifact_rules(artifact_type: str) -> tuple[set[str], int]:
    rules = {
        "archive": (ARCHIVE_EXTENSIONS, MAX_ARCHIVE_SIZE),
        "documentation": (DOCUMENT_EXTENSIONS, MAX_DEFAULT_SIZE),
        "presentation": (PRESENTATION_EXTENSIONS, MAX_DEFAULT_SIZE),
        "screencast": (VIDEO_EXTENSIONS, MAX_VIDEO_SIZE),
    }
    if artifact_type not in rules:
        raise ValueError(f"Unknown artifact type: {artifact_type}")
    return rules[artifact_type]


async def save_upload(file: UploadFile, subfolder: str, artifact_type: str) -> str:
    allowed_extensions, max_size = artifact_rules(artifact_type)
    filename = sanitize_filename(file.filename or "")
    extension = detect_extension(filename)
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {allowed}",
        )

    target_dir = Path(settings.upload_dir) / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / filename
    total_size = 0
    with target_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > max_size:
                output.close()
                os.remove(target_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Uploaded file is too large",
                )
            output.write(chunk)

    return str(target_path)
