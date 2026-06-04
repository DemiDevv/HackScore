from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.algo_task import AlgoTask, AlgoTest
from app.models.criterion import Criterion
from app.models.enums import HackathonStatus, UserRole
from app.models.hackathon import Hackathon
from app.models.team import Team, TeamMember
from app.models.user import User
from app.utils.security import hash_password


USERS = [
    ("admin@hackscore.ru", "admin123", "Алексей Организатор", UserRole.organizer),
    ("jury1@hackscore.ru", "jury123", "Анна Жюри", UserRole.jury),
    ("jury2@hackscore.ru", "jury123", "Дмитрий Эксперт", UserRole.jury),
    ("team1@hackscore.ru", "team123", "Иван Участник", UserRole.participant),
    ("team2@hackscore.ru", "team123", "Мария Участник", UserRole.participant),
    ("team3@hackscore.ru", "team123", "Павел Участник", UserRole.participant),
]

CRITERIA = [
    ("Полнота MVP", 0.20, True),
    ("Качество автопроверок", 0.15, False),
    ("Алгоритмический модуль", 0.10, False),
    ("Архитектура и качество кода", 0.10, True),
    ("UX/UI", 0.10, False),
    ("Работоспособность стенда", 0.10, False),
    ("Документация", 0.07, True),
    ("Презентация и скринкаст", 0.06, True),
    ("Инновационность", 0.06, False),
    ("Очная защита", 0.06, False),
]


async def get_or_create_user(db: AsyncSession, email: str, password: str, full_name: str, role: UserRole) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(email=email, password_hash=hash_password(password), full_name=full_name, role=role)
    db.add(user)
    await db.flush()
    return user


async def seed_database(db: AsyncSession) -> dict[str, int | str]:
    users = {}
    for email, password, full_name, role in USERS:
        users[email] = await get_or_create_user(db, email, password, full_name, role)

    admin = users["admin@hackscore.ru"]
    result = await db.execute(select(Hackathon).where(Hackathon.title == "Чемпионат по продуктовому программированию 2026"))
    hackathon = result.scalar_one_or_none()
    if hackathon is None:
        now = datetime.now(UTC)
        hackathon = Hackathon(
            title="Чемпионат по продуктовому программированию 2026",
            description="Демо-хакатон HackScore для проверки продуктовых решений.",
            status=HackathonStatus.in_progress,
            start_date=now,
            end_date=now + timedelta(days=2),
            created_by=admin.id,
        )
        db.add(hackathon)
        await db.flush()

    criteria_created = 0
    existing_criteria = await db.execute(select(Criterion).where(Criterion.hackathon_id == hackathon.id))
    existing_names = {criterion.name for criterion in existing_criteria.scalars().all()}
    for index, (name, weight, is_auto) in enumerate(CRITERIA):
        if name in existing_names:
            continue
        db.add(
            Criterion(
                hackathon_id=hackathon.id,
                name=name,
                description=f"Критерий оценки: {name}",
                weight=weight,
                max_score=10,
                is_auto=is_auto,
                order_index=index,
            )
        )
        criteria_created += 1

    teams_created = 0
    for index, email in enumerate(["team1@hackscore.ru", "team2@hackscore.ru", "team3@hackscore.ru"], start=1):
        result = await db.execute(select(Team).where(Team.hackathon_id == hackathon.id, Team.name == f"Команда {index}"))
        team = result.scalar_one_or_none()
        if team is None:
            team = Team(name=f"Команда {index}", hackathon_id=hackathon.id)
            db.add(team)
            await db.flush()
            db.add(TeamMember(team_id=team.id, user_id=users[email].id, is_captain=True))
            teams_created += 1

    tasks_created = await seed_algo_tasks(db, hackathon.id, admin.id)
    await db.commit()

    return {
        "status": "ok",
        "users": len(users),
        "criteria_created": criteria_created,
        "teams_created": teams_created,
        "algo_tasks_created": tasks_created,
    }


async def seed_algo_tasks(db: AsyncSession, hackathon_id, admin_id) -> int:
    created = 0
    result = await db.execute(select(AlgoTask).where(AlgoTask.hackathon_id == hackathon_id))
    existing_titles = {task.title for task in result.scalars().all()}

    if "Сумма двух чисел" not in existing_titles:
        task = AlgoTask(
            hackathon_id=hackathon_id,
            title="Сумма двух чисел",
            description="Даны два целых числа. Выведите их сумму.",
            time_limit_ms=1000,
            memory_limit_mb=256,
            created_by=admin_id,
        )
        db.add(task)
        await db.flush()
        tests = [("1 2\n", "3\n", True), ("10 15\n", "25\n", False), ("-5 8\n", "3\n", False), ("0 0\n", "0\n", False), ("100 200\n", "300\n", False)]
        for index, (input_data, expected_output, is_sample) in enumerate(tests):
            db.add(AlgoTest(task_id=task.id, input_data=input_data, expected_output=expected_output, is_sample=is_sample, order_index=index))
        created += 1

    if "Палиндром" not in existing_titles:
        task = AlgoTask(
            hackathon_id=hackathon_id,
            title="Палиндром",
            description="Дана строка. Выведите YES, если она палиндром, иначе NO.",
            time_limit_ms=1000,
            memory_limit_mb=256,
            created_by=admin_id,
        )
        db.add(task)
        await db.flush()
        tests = [("level\n", "YES\n", True), ("hello\n", "NO\n", False), ("abba\n", "YES\n", False), ("abcba\n", "YES\n", False), ("hack\n", "NO\n", False)]
        for index, (input_data, expected_output, is_sample) in enumerate(tests):
            db.add(AlgoTest(task_id=task.id, input_data=input_data, expected_output=expected_output, is_sample=is_sample, order_index=index))
        created += 1

    return created
