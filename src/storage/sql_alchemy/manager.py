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

                user_data = user.model_dump(exclude_none=True)

                stmt = insert(UserORM).values(**user_data)

                update_cols = {
                    key: getattr(stmt.excluded, key)
                    for key in user_data.keys()
                    if key != 'id'
                }

                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=['id'], set_=update_cols
                )

                await session.execute(upsert_stmt)

    async def update_user_data(self, user_id: int, fields: dict) -> None:
        user = User(id=user_id, **fields)
        await self.save_user(user)

    async def update_ai_settings(self, user_id: int, fields: dict) -> None:
        """
        Оновлює або створює налаштування AI для конкретного користувача(UPSERT).
        """
        async with self.session_factory() as session:
            async with session.begin():
                for model_name, values in fields.items():

                    insert_data = {
                        "user_id": user_id,
                        "model_name": model_name,
                        **values,
                    }

                    stmt = insert(AISettingORM).values(**insert_data)

                    update_dict = {
                        k: v for k, v in values.items() if k in ["token", "prompt"]
                    }

                    upsert_stmt = stmt.on_conflict_do_update(
                        index_elements=['user_id', 'model_name'], set_=update_dict
                    )

                    await session.execute(upsert_stmt)
