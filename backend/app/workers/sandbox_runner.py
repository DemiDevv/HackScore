import asyncio
import os
import resource
import subprocess
import tempfile
import time
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.algo_task import AlgoSubmission, AlgoTask
from app.models.enums import AlgoLanguage, AlgoVerdict
from app.workers.celery_app import celery_app


def limit_resources(memory_limit_mb: int) -> None:
    memory_bytes = memory_limit_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))


def write_source(workdir: Path, language: AlgoLanguage, source_code: str) -> Path:
    filenames = {
        AlgoLanguage.python: "solution.py",
        AlgoLanguage.cpp: "solution.cpp",
        AlgoLanguage.java: "Solution.java",
    }
    path = workdir / filenames[language]
    path.write_text(source_code, encoding="utf-8")
    return path


def compile_solution(workdir: Path, language: AlgoLanguage, memory_limit_mb: int) -> tuple[AlgoVerdict | None, str | None]:
    if language == AlgoLanguage.cpp:
        result = subprocess.run(
            ["g++", "-O2", "-std=c++17", "-o", "solution", "solution.cpp"],
            cwd=workdir,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
            preexec_fn=lambda: limit_resources(memory_limit_mb),
        )
        if result.returncode != 0:
            return AlgoVerdict.CE, result.stderr[:2000]
    elif language == AlgoLanguage.java:
        result = subprocess.run(
            ["javac", "Solution.java"],
            cwd=workdir,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
            preexec_fn=lambda: limit_resources(memory_limit_mb),
        )
        if result.returncode != 0:
            return AlgoVerdict.CE, result.stderr[:2000]
    return None, None


def run_command_for_language(language: AlgoLanguage) -> list[str]:
    if language == AlgoLanguage.python:
        return ["python3", "solution.py"]
    if language == AlgoLanguage.cpp:
        return ["./solution"]
    return ["java", "Solution"]


def run_single_test(
    workdir: Path,
    language: AlgoLanguage,
    input_data: str,
    expected_output: str,
    time_limit_ms: int,
    memory_limit_mb: int,
) -> tuple[AlgoVerdict, int, str | None]:
    started = time.perf_counter()
    try:
        result = subprocess.run(
            run_command_for_language(language),
            cwd=workdir,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=max(time_limit_ms / 1000, 0.001),
            check=False,
            preexec_fn=lambda: limit_resources(memory_limit_mb),
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return AlgoVerdict.TL, elapsed_ms, "Time limit exceeded"

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    if result.returncode != 0:
        return AlgoVerdict.RE, elapsed_ms, result.stderr[:2000]
    if result.stdout.strip() != expected_output.strip():
        return AlgoVerdict.WA, elapsed_ms, "Wrong answer"
    return AlgoVerdict.OK, elapsed_ms, None


async def load_submission(submission_id: UUID) -> AlgoSubmission:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AlgoSubmission)
            .where(AlgoSubmission.id == submission_id)
            .options(selectinload(AlgoSubmission.task).selectinload(AlgoTask.tests))
        )
        submission = result.scalar_one_or_none()
        if submission is None:
            raise RuntimeError("Algorithm submission not found")
        return submission


async def save_result(
    submission_id: UUID,
    verdict: AlgoVerdict,
    passed: int,
    total: int,
    execution_time: int | None,
    memory_used: int | None,
    error_message: str | None,
) -> None:
    async with AsyncSessionLocal() as db:
        submission = await db.get(AlgoSubmission, submission_id)
        if submission is None:
            return
        submission.verdict = verdict
        submission.test_passed = passed
        submission.test_total = total
        submission.execution_time = execution_time
        submission.memory_used = memory_used
        submission.error_message = error_message
        await db.commit()


async def run_solution(submission_id: str) -> None:
    submission = await load_submission(UUID(submission_id))
    task = submission.task
    tests = [test for test in task.tests if not test.is_sample] or list(task.tests)

    if not tests:
        await save_result(submission.id, AlgoVerdict.CE, 0, 0, None, None, "No tests configured")
        return

    with tempfile.TemporaryDirectory(prefix="hackscore-algo-") as temp_dir:
        workdir = Path(temp_dir)
        write_source(workdir, submission.language, submission.source_code)
        compile_verdict, compile_error = compile_solution(workdir, submission.language, task.memory_limit_mb)
        if compile_verdict is not None:
            await save_result(submission.id, compile_verdict, 0, len(tests), None, None, compile_error)
            return

        passed = 0
        max_time = 0
        final_verdict = AlgoVerdict.OK
        error_message = None

        for test in tests:
            verdict, elapsed_ms, error = run_single_test(
                workdir,
                submission.language,
                test.input_data,
                test.expected_output,
                task.time_limit_ms,
                task.memory_limit_mb,
            )
            max_time = max(max_time, elapsed_ms)
            if verdict != AlgoVerdict.OK:
                final_verdict = verdict
                error_message = error
                break
            passed += 1

        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        memory_used = int(usage.ru_maxrss)
        if os.uname().sysname == "Darwin":
            memory_used = int(memory_used / 1024)

        await save_result(
            submission.id,
            final_verdict,
            passed,
            len(tests),
            max_time,
            memory_used,
            error_message,
        )


@celery_app.task(name="app.workers.sandbox_runner.run_algo_solution")
def run_algo_solution(submission_id: str) -> None:
    asyncio.run(run_solution(submission_id))
