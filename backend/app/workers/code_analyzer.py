import asyncio
import json
import re
import subprocess
import tarfile
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.check_result import CheckResult
from app.models.enums import CheckStatus, CheckType
from app.models.submission import Submission
from app.workers.celery_app import celery_app


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".kt",
    ".swift",
}

SECRET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"api[_-]?key\s*=\s*['\"]?[^'\"\s]{12,}",
        r"secret\s*=\s*['\"]?[^'\"\s]{12,}",
        r"password\s*=\s*['\"]?[^'\"\s]{8,}",
        r"aws_access_key_id\s*=\s*['\"]?[^'\"\s]{12,}",
        r"aws_secret_access_key\s*=\s*['\"]?[^'\"\s]{20,}",
    ]
]

IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}


def run_command(command: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def prepare_source(submission: Submission, workspace: Path) -> Path:
    source_dir = workspace / "source"

    if submission.repo_url:
        result = run_command(["git", "clone", "--depth", "1", submission.repo_url, str(source_dir)], workspace, timeout=120)
        if result is None or result.returncode != 0:
            stderr = result.stderr.strip() if result is not None else "git is not available"
            raise RuntimeError(f"Failed to clone repository: {stderr}")
        return source_dir

    if submission.repo_archive:
        archive_path = Path(submission.repo_archive)
        if not archive_path.exists():
            raise RuntimeError("Repository archive file not found")

        source_dir.mkdir(parents=True, exist_ok=True)
        if archive_path.name.lower().endswith(".zip"):
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(source_dir)
        elif archive_path.name.lower().endswith(".tar.gz"):
            with tarfile.open(archive_path, "r:gz") as archive:
                archive.extractall(source_dir, filter="data")
        else:
            raise RuntimeError("Unsupported repository archive")
        return source_dir

    raise RuntimeError("Submission does not contain repository URL or archive")


def iter_source_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in CODE_EXTENSIONS:
            files.append(path)
    return files


def check_structure(source_dir: Path) -> tuple[float, dict[str, bool]]:
    root_files = {path.name.lower() for path in source_dir.iterdir() if path.is_file()}
    checks = {
        "readme": "readme.md" in root_files or "readme.rst" in root_files,
        "license": any(name.startswith("license") for name in root_files),
        "manifest": any(
            name in root_files
            for name in ["requirements.txt", "package.json", "cargo.toml", "go.mod", "pyproject.toml", "pom.xml"]
        ),
        "docker": "dockerfile" in root_files or "docker-compose.yml" in root_files,
        "gitignore": ".gitignore" in root_files,
    }
    raw_score = (
        (2.0 if checks["readme"] else 0.0)
        + (0.5 if checks["license"] else 0.0)
        + (1.0 if checks["manifest"] else 0.0)
        + (1.0 if checks["docker"] else 0.0)
        + (0.5 if checks["gitignore"] else 0.0)
    )
    return min(10.0, raw_score * 2), checks


def count_loc(files: list[Path]) -> int:
    total = 0
    for path in files:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                total += sum(1 for line in handle if line.strip())
        except OSError:
            continue
    return total


def analyze_python(files: list[Path]) -> dict[str, float | int | None]:
    complexities: list[float] = []
    maintainability: list[float] = []

    for path in files:
        if path.suffix.lower() != ".py":
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        complexities.extend(block.complexity for block in cc_visit(source))
        maintainability.append(mi_visit(source, multi=True))

    avg_complexity = sum(complexities) / len(complexities) if complexities else None
    avg_mi = sum(maintainability) / len(maintainability) if maintainability else None
    return {
        "python_files": sum(1 for path in files if path.suffix.lower() == ".py"),
        "avg_complexity": round(avg_complexity, 2) if avg_complexity is not None else None,
        "avg_maintainability_index": round(avg_mi, 2) if avg_mi is not None else None,
    }


def run_pylint(source_dir: Path, python_files: list[Path]) -> dict[str, int | bool]:
    if not python_files:
        return {"available": False, "messages": 0, "errors": 0, "warnings": 0}

    result = run_command(["pylint", "--output-format=json", *[str(path) for path in python_files[:80]]], source_dir, timeout=90)
    if result is None:
        return {"available": False, "messages": 0, "errors": 0, "warnings": 0}

    try:
        messages = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        messages = []

    return {
        "available": True,
        "messages": len(messages),
        "errors": sum(1 for item in messages if item.get("type") in {"error", "fatal"}),
        "warnings": sum(1 for item in messages if item.get("type") == "warning"),
    }


def run_eslint(source_dir: Path) -> dict[str, int | bool]:
    if not (source_dir / "package.json").exists():
        return {"available": False, "messages": 0, "errors": 0, "warnings": 0}

    eslint_bin = source_dir / "node_modules" / ".bin" / "eslint"
    if not eslint_bin.exists():
        return {"available": False, "messages": 0, "errors": 0, "warnings": 0}

    result = run_command([str(eslint_bin), ".", "--format", "json"], source_dir, timeout=90)
    if result is None:
        return {"available": False, "messages": 0, "errors": 0, "warnings": 0}

    try:
        reports = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        reports = []

    return {
        "available": True,
        "messages": sum(len(report.get("messages", [])) for report in reports),
        "errors": sum(report.get("errorCount", 0) for report in reports),
        "warnings": sum(report.get("warningCount", 0) for report in reports),
    }


def scan_secrets(files: list[Path], source_dir: Path) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                findings.append({"file": str(path.relative_to(source_dir)), "line": line_number})
                break

    for env_file in source_dir.rglob(".env*"):
        if env_file.is_file() and ".git" not in env_file.parts:
            findings.append({"file": str(env_file.relative_to(source_dir)), "line": 1})

    return findings[:50]


def complexity_score(avg_complexity: float | None) -> float:
    if avg_complexity is None:
        return 7.0
    if avg_complexity <= 5:
        return 10.0
    if avg_complexity <= 10:
        return 8.0
    if avg_complexity <= 15:
        return 5.0
    return 2.0


def lint_score(lint_messages: int, loc: int) -> float:
    if loc == 0:
        return 5.0
    per_100_loc = lint_messages / max(loc / 100, 1)
    return max(0.0, round(10.0 - per_100_loc, 2))


def analyze_source(source_dir: Path) -> tuple[float, dict[str, object]]:
    files = iter_source_files(source_dir)
    loc = count_loc(files)
    structure_score, structure = check_structure(source_dir)
    python_metrics = analyze_python(files)
    python_files = [path for path in files if path.suffix.lower() == ".py"]
    pylint_report = run_pylint(source_dir, python_files)
    eslint_report = run_eslint(source_dir)
    secrets = scan_secrets(files, source_dir)

    lint_messages = int(pylint_report["messages"]) + int(eslint_report["messages"])
    scores = {
        "structure": round(structure_score, 2),
        "complexity": complexity_score(python_metrics["avg_complexity"]),
        "lint": lint_score(lint_messages, loc),
    }
    secrets_penalty = min(6.0, len(secrets) * 2.0)
    total = max(0.0, min(10.0, scores["structure"] * 0.35 + scores["complexity"] * 0.3 + scores["lint"] * 0.35 - secrets_penalty))

    report = {
        "structure": structure,
        "metrics": {
            "loc": loc,
            "files": len(files),
            **python_metrics,
        },
        "lint": {
            "pylint": pylint_report,
            "eslint": eslint_report,
            "messages_total": lint_messages,
        },
        "security": {
            "secrets_found": len(secrets),
            "findings": secrets,
            "penalty": secrets_penalty,
        },
        "scores": scores,
    }
    return round(total, 2), report


async def get_code_check(submission_id: UUID) -> tuple[Submission, CheckResult]:
    async with AsyncSessionLocal() as db:
        submission = await db.get(Submission, submission_id)
        if submission is None:
            raise RuntimeError("Submission not found")

        result = await db.execute(
            select(CheckResult).where(
                CheckResult.submission_id == submission_id,
                CheckResult.check_type == CheckType.code,
            )
        )
        check = result.scalar_one_or_none()
        if check is None:
            check = CheckResult(submission_id=submission_id, check_type=CheckType.code, status=CheckStatus.pending)
            db.add(check)
            await db.commit()
            await db.refresh(check)

        return submission, check


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


async def mark_running(check_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        check = await db.get(CheckResult, check_id)
        if check is None:
            return
        check.status = CheckStatus.running
        check.started_at = datetime.now(UTC)
        await db.commit()


async def run_analysis(submission_id: str) -> None:
    submission, check = await get_code_check(UUID(submission_id))
    await mark_running(check.id)

    try:
        with tempfile.TemporaryDirectory(prefix="hackscore-code-") as temp_dir:
            source_dir = prepare_source(submission, Path(temp_dir))
            score, report = analyze_source(source_dir)
        await save_check_result(check.id, CheckStatus.completed, score, report)
    except Exception as exc:
        await save_check_result(check.id, CheckStatus.failed, None, {"error": str(exc)})


@celery_app.task(name="app.workers.code_analyzer.analyze_code")
def analyze_code(submission_id: str) -> None:
    asyncio.run(run_analysis(submission_id))
