# -*- coding: utf-8 -*-

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from src.config.postgres import settings
from src.storage.sql_alchemy.models import Base


async def init_models():

    engine = create_async_engine(settings.url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_models())
