from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.check_result import CheckResult
from app.models.enums import CheckStatus, CheckType
from app.models.submission import Submission
from app.schemas.score import AIReviewResponse


MODEL_NAME = "HackScore AI Review Model"
MODEL_VERSION = "0.1.0"


@dataclass(frozen=True)
class ReviewSignals:
    code_quality: float
    documentation_quality: float
    pitch_quality: float
    demo_readiness: float
    risk_level: float
    completed_checks_ratio: float
    artifact_coverage: float


FEATURE_WEIGHTS = {
    "code_quality": 0.28,
    "documentation_quality": 0.2,
    "pitch_quality": 0.2,
    "demo_readiness": 0.18,
    "risk_level": -0.14,
}


def build_ai_review(submission: Submission) -> AIReviewResponse:
    checks = {check.check_type: check for check in submission.check_results}
    signals = extract_signals(submission, checks)
    score = score_signals(signals)
    strengths = build_strengths(submission, checks, signals)
    risks = build_risks(submission, checks, signals)
    missing_parts = build_missing_parts(submission, checks)
    jury_questions = build_jury_questions(signals, risks, missing_parts)

    verdict = verdict_for_score(score, signals.risk_level)
    confidence = confidence_for_signals(signals)

    return AIReviewResponse(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        score=round(score, 2),
        confidence=confidence,
        verdict=verdict,
        summary=build_summary(score, verdict, strengths, risks),
        strengths=strengths,
        risks=risks,
        missing_parts=missing_parts,
        jury_questions=jury_questions,
        feature_weights=FEATURE_WEIGHTS,
        signals={
            "code_quality": round(signals.code_quality, 3),
            "documentation_quality": round(signals.documentation_quality, 3),
            "pitch_quality": round(signals.pitch_quality, 3),
            "demo_readiness": round(signals.demo_readiness, 3),
            "risk_level": round(signals.risk_level, 3),
            "completed_checks_ratio": round(signals.completed_checks_ratio, 3),
            "artifact_coverage": round(signals.artifact_coverage, 3),
        },
    )


def extract_signals(submission: Submission, checks: dict[CheckType, CheckResult]) -> ReviewSignals:
    code = checks.get(CheckType.code)
    documentation = checks.get(CheckType.documentation)
    presentation = checks.get(CheckType.presentation)
    screencast = checks.get(CheckType.screencast)

    code_quality = score_signal(code, fallback=0.45)
    documentation_quality = score_signal(documentation, fallback=0.35)
    pitch_quality = average_present(
        [
            score_signal(presentation, fallback=None),
            score_signal(screencast, fallback=None),
        ],
        fallback=0.35,
    )
    artifact_coverage = artifact_coverage_signal(submission)
    demo_readiness = demo_readiness_signal(submission, checks, artifact_coverage)
    completed_checks_ratio = completed_checks_signal(checks)
    risk_level = risk_signal(submission, checks, completed_checks_ratio, artifact_coverage)

    return ReviewSignals(
        code_quality=code_quality,
        documentation_quality=documentation_quality,
        pitch_quality=pitch_quality,
        demo_readiness=demo_readiness,
        risk_level=risk_level,
        completed_checks_ratio=completed_checks_ratio,
        artifact_coverage=artifact_coverage,
    )


def score_signal(check: CheckResult | None, fallback: float | None) -> float | None:
    if check is None or check.status != CheckStatus.completed or check.score is None:
        return fallback
    return clamp(check.score / 10)


def average_present(values: list[float | None], fallback: float) -> float:
    present = [value for value in values if value is not None]
    if not present:
        return fallback
    return clamp(sum(present) / len(present))


def artifact_coverage_signal(submission: Submission) -> float:
    artifacts = [
        bool(submission.repo_url or submission.repo_archive),
        bool(submission.doc_file),
        bool(submission.presentation),
        bool(submission.screencast_file or submission.screencast_url),
    ]
    return sum(1 for artifact in artifacts if artifact) / len(artifacts)


def demo_readiness_signal(
    submission: Submission,
    checks: dict[CheckType, CheckResult],
    artifact_coverage: float,
) -> float:
    code_report = report_for(checks.get(CheckType.code))
    structure = dict_value(code_report, "structure")
    has_docker = bool(structure.get("docker")) if isinstance(structure, dict) else False
    has_readme = bool(structure.get("readme")) if isinstance(structure, dict) else False

    video_report = report_for(checks.get(CheckType.screencast))
    external_video = bool(video_report.get("external_link"))
    has_demo_video = bool(submission.screencast_file or submission.screencast_url or external_video)

    readiness = artifact_coverage * 0.45
    readiness += (0.2 if has_docker else 0.0)
    readiness += (0.15 if has_readme else 0.0)
    readiness += (0.2 if has_demo_video else 0.0)
    return clamp(readiness)


def completed_checks_signal(checks: dict[CheckType, CheckResult]) -> float:
    expected = [CheckType.code, CheckType.documentation, CheckType.presentation, CheckType.screencast]
    completed = sum(1 for check_type in expected if checks.get(check_type) and checks[check_type].status == CheckStatus.completed)
    return completed / len(expected)


def risk_signal(
    submission: Submission,
    checks: dict[CheckType, CheckResult],
    completed_checks_ratio: float,
    artifact_coverage: float,
) -> float:
    risk = 0.0
    risk += (1.0 - completed_checks_ratio) * 0.28
    risk += (1.0 - artifact_coverage) * 0.24

    failed_checks = sum(1 for check in checks.values() if check.status == CheckStatus.failed)
    risk += min(0.24, failed_checks * 0.08)

    code_report = report_for(checks.get(CheckType.code))
    security = dict_value(code_report, "security")
    secrets_found = int_value(security.get("secrets_found") if isinstance(security, dict) else None)
    risk += min(0.28, secrets_found * 0.14)

    lint = dict_value(code_report, "lint")
    messages_total = int_value(lint.get("messages_total") if isinstance(lint, dict) else None)
    metrics = dict_value(code_report, "metrics")
    loc = int_value(metrics.get("loc") if isinstance(metrics, dict) else None)
    if loc > 0:
        messages_per_100_loc = messages_total / max(loc / 100, 1)
        if messages_per_100_loc > 6:
            risk += 0.12

    if not (submission.repo_url or submission.repo_archive):
        risk += 0.08
    return clamp(risk)


def score_signals(signals: ReviewSignals) -> float:
    positive = (
        signals.code_quality * FEATURE_WEIGHTS["code_quality"]
        + signals.documentation_quality * FEATURE_WEIGHTS["documentation_quality"]
        + signals.pitch_quality * FEATURE_WEIGHTS["pitch_quality"]
        + signals.demo_readiness * FEATURE_WEIGHTS["demo_readiness"]
    )
    positive_weight = sum(weight for weight in FEATURE_WEIGHTS.values() if weight > 0)
    risk_penalty = signals.risk_level * abs(FEATURE_WEIGHTS["risk_level"])
    return clamp(positive / positive_weight - risk_penalty) * 10


def build_strengths(
    submission: Submission,
    checks: dict[CheckType, CheckResult],
    signals: ReviewSignals,
) -> list[str]:
    strengths: list[str] = []
    if signals.code_quality >= 0.75:
        strengths.append("Кодовая база выглядит достаточно зрелой по автоматическим метрикам.")
    if signals.documentation_quality >= 0.7:
        strengths.append("Документация покрывает ключевые разделы и помогает быстрее проверить решение.")
    if signals.pitch_quality >= 0.7:
        strengths.append("Презентация и демо хорошо поддерживают экспертную оценку проекта.")
    if signals.demo_readiness >= 0.7:
        strengths.append("Есть признаки готовности стенда к запуску и демонстрации.")

    code_report = report_for(checks.get(CheckType.code))
    structure = dict_value(code_report, "structure")
    if isinstance(structure, dict) and structure.get("docker"):
        strengths.append("В репозитории найден Docker, это снижает риск проблем с воспроизведением.")
    if submission.screencast_url or submission.screencast_file:
        strengths.append("Команда приложила скринкаст, жюри может проверить сценарий использования.")

    return strengths[:5] or ["Модель видит базовую комплектность сабмита, но сильные стороны требуют экспертного подтверждения."]


def build_risks(
    submission: Submission,
    checks: dict[CheckType, CheckResult],
    signals: ReviewSignals,
) -> list[str]:
    risks: list[str] = []
    if signals.risk_level >= 0.55:
        risks.append("Сабмит имеет повышенный интегральный риск: часть артефактов или проверок выглядит неполной.")

    failed = [check.check_type.value for check in checks.values() if check.status == CheckStatus.failed]
    if failed:
        risks.append(f"Есть упавшие автоматические проверки: {', '.join(failed)}.")

    code_report = report_for(checks.get(CheckType.code))
    security = dict_value(code_report, "security")
    secrets_found = int_value(security.get("secrets_found") if isinstance(security, dict) else None)
    if secrets_found:
        risks.append(f"Найдены потенциальные секреты в коде: {secrets_found}.")

    metrics = dict_value(code_report, "metrics")
    loc = int_value(metrics.get("loc") if isinstance(metrics, dict) else None)
    if submission.repo_url or submission.repo_archive:
        if loc < 80 and checks.get(CheckType.code) is not None:
            risks.append("Объем найденного кода низкий, стоит проверить полноту реализации вручную.")

    documentation = checks.get(CheckType.documentation)
    if documentation and documentation.score is not None and documentation.score < 5:
        risks.append("Документация получила низкую автоматическую оценку.")

    presentation = checks.get(CheckType.presentation)
    if presentation and presentation.score is not None and presentation.score < 5:
        risks.append("Презентация может не раскрывать проблему, решение или целевую аудиторию.")

    return risks[:5] or ["Критичных автоматических рисков модель не выделила."]


def build_missing_parts(submission: Submission, checks: dict[CheckType, CheckResult]) -> list[str]:
    missing: list[str] = []
    if not (submission.repo_url or submission.repo_archive):
        missing.append("репозиторий или архив с кодом")
    if not submission.doc_file:
        missing.append("документация")
    if not submission.presentation:
        missing.append("презентация")
    if not (submission.screencast_file or submission.screencast_url):
        missing.append("скринкаст")

    expected_checks = {
        CheckType.code: "автопроверка кода",
        CheckType.documentation: "автопроверка документации",
        CheckType.presentation: "автопроверка презентации",
        CheckType.screencast: "автопроверка скринкаста",
    }
    for check_type, label in expected_checks.items():
        check = checks.get(check_type)
        if check is None or check.status in {CheckStatus.pending, CheckStatus.running}:
            missing.append(label)

    return missing[:7]


def build_jury_questions(signals: ReviewSignals, risks: list[str], missing_parts: list[str]) -> list[str]:
    questions: list[str] = []
    if signals.demo_readiness < 0.6:
        questions.append("Может ли команда быстро поднять проект на чистом окружении во время защиты?")
    if signals.code_quality < 0.55:
        questions.append("Какие части реализации являются рабочим MVP, а какие остались прототипом?")
    if signals.documentation_quality < 0.55:
        questions.append("Достаточно ли документации, чтобы другой разработчик воспроизвел запуск проекта?")
    if signals.pitch_quality < 0.55:
        questions.append("Ясно ли команда объясняет проблему, пользователя и ценность решения?")
    if missing_parts:
        questions.append("Почему отсутствуют или не проверены ключевые артефакты сабмита?")
    if risks and risks != ["Критичных автоматических рисков модель не выделила."]:
        questions.append("Какие риски из AI-рецензии команда готова закрыть в первую очередь?")

    return questions[:5] or ["Какая часть проекта дает основную продуктовую ценность уже сейчас?"]


def verdict_for_score(score: float, risk_level: float) -> str:
    if score >= 8 and risk_level < 0.35:
        return "strong_candidate"
    if score >= 6.5:
        return "promising"
    if score >= 4.5:
        return "needs_manual_review"
    return "high_risk"


def confidence_for_signals(signals: ReviewSignals) -> float:
    confidence = signals.completed_checks_ratio * 0.65 + signals.artifact_coverage * 0.35
    return round(clamp(confidence), 2)


def build_summary(score: float, verdict: str, strengths: list[str], risks: list[str]) -> str:
    verdict_text = {
        "strong_candidate": "сильный кандидат",
        "promising": "перспективный проект",
        "needs_manual_review": "требует внимательной ручной проверки",
        "high_risk": "высокорисковый сабмит",
    }[verdict]
    main_strength = strengths[0].rstrip(".")
    main_risk = risks[0].rstrip(".")
    return f"AI-модель оценивает проект как {verdict_text}: {score:.1f}/10. {main_strength}. {main_risk}."


def report_for(check: CheckResult | None) -> dict[str, Any]:
    if check is None or not isinstance(check.report, dict):
        return {}
    return check.report


def dict_value(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def int_value(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
