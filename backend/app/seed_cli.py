import asyncio

from app.database import AsyncSessionLocal
from app.seed import seed_database


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_database(db)


if __name__ == "__main__":
    asyncio.run(main())
