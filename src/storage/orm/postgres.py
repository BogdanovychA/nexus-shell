# -*- coding: utf-8 -*-

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from src.config.postgres import settings
from src.storage.orm.models import Base

DATABASE_URL = f"postgresql+asyncpg://{settings.user}:{settings.password}@{settings.server}:{settings.port}/{settings.db}"


async def init_models():

    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_models())
