import asyncio
import json
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.check_result import CheckResult
from app.models.enums import CheckStatus, CheckType
from app.models.submission import Submission
from app.workers.celery_app import celery_app


def run_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def duration_score(duration_sec: float | None) -> float:
    if duration_sec is None:
        return 5.0
    if duration_sec < 60:
        return 3.0
    if duration_sec < 180:
        return 7.0
    if duration_sec <= 300:
        return 10.0
    if duration_sec <= 600:
        return 7.0
    return 5.0


def probe_video(path: Path) -> dict[str, object]:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
    )
    if result is None or result.returncode != 0:
        raise RuntimeError("ffprobe failed or is not available")

    data = json.loads(result.stdout or "{}")
    streams = data.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
    duration = data.get("format", {}).get("duration") or video_stream.get("duration")

    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)

    return {
        "duration_sec": round(float(duration), 2) if duration is not None else None,
        "width": width or None,
        "height": height or None,
        "resolution": f"{width}x{height}" if width and height else None,
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "has_audio": bool(audio_stream),
        "file_size": path.stat().st_size,
    }


def quality_bonus(metadata: dict[str, object]) -> float:
    height = metadata.get("height")
    has_audio = bool(metadata.get("has_audio"))
    bonus = 0.0
    if isinstance(height, int) and height >= 1080:
        bonus += 1.0
    elif isinstance(height, int) and height >= 720:
        bonus += 0.5
    if has_audio:
        bonus += 1.0
    return bonus


def transcribe_video(path: Path, has_audio: bool) -> dict[str, object]:
    if not has_audio:
        return {"enabled": False, "transcript_preview": None, "word_count": 0, "summary": None}
    if os.getenv("HACKSCORE_ENABLE_WHISPER", "false").lower() != "true":
        return {"enabled": False, "transcript_preview": None, "word_count": 0, "summary": None}

    with tempfile.TemporaryDirectory(prefix="hackscore-video-") as temp_dir:
        audio_path = Path(temp_dir) / "audio.wav"
        ffmpeg = run_command(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                str(audio_path),
            ],
            timeout=180,
        )
        if ffmpeg is None or ffmpeg.returncode != 0:
            return {"enabled": True, "error": "ffmpeg audio extraction failed"}

        try:
            import whisper

            model = whisper.load_model("base")
            result = model.transcribe(str(audio_path), language="ru")
        except Exception as exc:
            return {"enabled": True, "error": str(exc)}

    transcript = str(result.get("text", "")).strip()
    words = transcript.split()
    preview = transcript[:500]
    return {
        "enabled": True,
        "transcript_preview": preview,
        "word_count": len(words),
        "summary": preview,
    }


def analyze_video(path: Path) -> tuple[float, dict[str, object]]:
    metadata = probe_video(path)
    base_score = duration_score(metadata["duration_sec"])
    bonus = quality_bonus(metadata)
    transcription = transcribe_video(path, bool(metadata["has_audio"]))
    score = min(10.0, base_score + bonus)

    report = {
        **metadata,
        "quality_bonus": bonus,
        "transcription": transcription,
        "scores": {
            "duration": base_score,
            "quality_bonus": bonus,
        },
    }
    return round(score, 2), report


async def get_video_check(submission_id: UUID) -> tuple[Submission, CheckResult]:
    async with AsyncSessionLocal() as db:
        submission = await db.get(Submission, submission_id)
        if submission is None:
            raise RuntimeError("Submission not found")

        result = await db.execute(
            select(CheckResult).where(
                CheckResult.submission_id == submission_id,
                CheckResult.check_type == CheckType.screencast,
            )
        )
        check = result.scalar_one_or_none()
        if check is None:
            check = CheckResult(
                submission_id=submission_id,
                check_type=CheckType.screencast,
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


async def run_processing(submission_id: str) -> None:
    submission, check = await get_video_check(UUID(submission_id))
    await mark_running(check.id)

    try:
        if submission.screencast_url and not submission.screencast_file:
            await save_check_result(
                check.id,
                CheckStatus.completed,
                5.0,
                {
                    "external_link": True,
                    "url": submission.screencast_url,
                    "detail": "External video links receive baseline score because automatic metadata checks are unavailable.",
                },
            )
            return

        if not submission.screencast_file:
            raise RuntimeError("Screencast file is missing")

        score, report = analyze_video(Path(submission.screencast_file))
        await save_check_result(check.id, CheckStatus.completed, score, report)
    except Exception as exc:
        await save_check_result(check.id, CheckStatus.failed, None, {"error": str(exc)})


@celery_app.task(name="app.workers.video_processor.process_video")
def process_video(submission_id: str) -> None:
    asyncio.run(run_processing(submission_id))
