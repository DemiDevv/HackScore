import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from docx import Document
from PyPDF2 import PdfReader
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.check_result import CheckResult
from app.models.enums import CheckStatus, CheckType
from app.models.submission import Submission
from app.workers.celery_app import celery_app


SECTION_PATTERNS = {
    "description": re.compile(r"(описание|description|о системе|about)", re.IGNORECASE),
    "deployment": re.compile(r"(разв[её]ртывание|deploy|установка|install)", re.IGNORECASE),
    "usage": re.compile(r"(эксплуатация|usage|использование)", re.IGNORECASE),
}


def read_pdf(path: Path) -> tuple[str, bool]:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    has_images = False

    for page in reader.pages:
        resources = page.get("/Resources") or {}
        x_objects = resources.get("/XObject") or {}
        try:
            objects = x_objects.get_object()
        except Exception:
            objects = {}
        for obj in objects.values():
            try:
                if obj.get_object().get("/Subtype") == "/Image":
                    has_images = True
                    break
            except Exception:
                continue
        if has_images:
            break

    return text, has_images


def read_docx(path: Path) -> tuple[str, bool]:
    document = Document(str(path))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    return text, len(document.inline_shapes) > 0


def read_markdown(path: Path) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    has_images = bool(re.search(r"!\[[^\]]*]\([^)]+\)", text))
    return text, has_images


def extract_document(path: Path) -> tuple[str, bool]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(path)
    if suffix == ".docx":
        return read_docx(path)
    if suffix == ".md":
        return read_markdown(path)
    raise RuntimeError("Unsupported documentation format")


def volume_score(length: int) -> float:
    if length < 500:
        return 0.0
    if length < 2000:
        return 3.0
    if length < 5000:
        return 7.0
    return 10.0


def analyze_document(path: Path) -> tuple[float, dict[str, object]]:
    text, has_images = extract_document(path)
    normalized = text.lower()
    sections = {name: bool(pattern.search(normalized)) for name, pattern in SECTION_PATTERNS.items()}

    section_score = sum(2.0 for found in sections.values() if found)
    size_score = volume_score(len(text))
    image_score = 2.0 if has_images else 0.0
    total = min(10.0, section_score + size_score * 0.25 + image_score)

    report = {
        "sections": sections,
        "length": len(text),
        "has_images": has_images,
        "scores": {
            "sections": section_score,
            "volume": size_score,
            "images": image_score,
        },
    }
    return round(total, 2), report


async def get_documentation_check(submission_id: UUID) -> tuple[Submission, CheckResult]:
    async with AsyncSessionLocal() as db:
        submission = await db.get(Submission, submission_id)
        if submission is None:
            raise RuntimeError("Submission not found")

        result = await db.execute(
            select(CheckResult).where(
                CheckResult.submission_id == submission_id,
                CheckResult.check_type == CheckType.documentation,
            )
        )
        check = result.scalar_one_or_none()
        if check is None:
            check = CheckResult(
                submission_id=submission_id,
                check_type=CheckType.documentation,
                status=CheckStatus.pending,
            )
            db.add(check)
            await db.commit()
            await db.refresh(check)
        return submission, check


async def mark_running(check_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        check = await db.get(CheckResult, check_id)
        if check is None:
            return
        check.status = CheckStatus.running
        check.started_at = datetime.now(UTC)
        await db.commit()


async def save_check_result(check_id: UUID, status_value: CheckStatus, score: float | None, report: dict[str, object]) -> None:
    async with AsyncSessionLocal() as db:
        check = await db.get(CheckResult, check_id)
        if check is None:
            return
        check.status = status_value
        check.score = score
        check.report = report
        check.completed_at = datetime.now(UTC)
        await db.commit()


async def run_validation(submission_id: str) -> None:
    submission, check = await get_documentation_check(UUID(submission_id))
    await mark_running(check.id)

    try:
        if not submission.doc_file:
            raise RuntimeError("Documentation file is missing")
        score, report = analyze_document(Path(submission.doc_file))
        await save_check_result(check.id, CheckStatus.completed, score, report)
    except Exception as exc:
        await save_check_result(check.id, CheckStatus.failed, None, {"error": str(exc)})


@celery_app.task(name="app.workers.doc_validator.validate_documentation")
def validate_documentation(submission_id: str) -> None:
    asyncio.run(run_validation(submission_id))
