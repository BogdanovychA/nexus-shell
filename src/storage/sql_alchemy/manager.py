# -*- coding: utf-8 -*-

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.models import User
from src.storage.sql_alchemy.models import AISettingORM, UserORM


class SQLAlchemyManager:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def save_user(self, user: User) -> None:
        """
        Зберігає або оновлює дані користувача (UPSERT).
        """
        async with self.session_factory() as session:
            async with session.begin():

                user_data = user.model_dump()

                stmt = insert(UserORM).values(**user_data)

                update_cols = {
                    col.name: col for col in stmt.excluded if col.name != 'id'
                }

                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=['id'], set_=update_cols
                )

                await session.execute(upsert_stmt)
