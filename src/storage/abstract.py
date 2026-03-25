# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import postgres
from src.storage.sql_alchemy.manager import SQLAlchemyManager
from storage import firebase

if TYPE_CHECKING:
    from models import User


class StorageManager(ABC):

    @abstractmethod
    async def save_user(self, user: User):
        """Збереження користувача в БД"""
        pass

    @abstractmethod
    async def load_user(self, user_id: int) -> User | None:
        """Завантаження користувача з БД"""
        pass

    @abstractmethod
    async def update_user_fields(self, user_id: int, fields: dict) -> None:
        """Оновлення даних користувача"""
        pass

    @abstractmethod
    async def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        """Завантаження даних користувача"""
        pass


class PostgresStorage(StorageManager):

    def __init__(self):
        self.engine = create_async_engine(postgres.settings.url, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.storage = SQLAlchemyManager(session_factory=self.async_session)

    async def save_user(self, user: User):
        await self.storage.save_user(user)

    async def load_user(self, user_id: int) -> User | None:
        pass

    async def update_user_fields(self, user_id: int, fields: dict) -> None:
        pass

    async def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        pass

    async def close(self):
        await self.engine.dispose()


class FirebaseStorage(StorageManager):

    async def save_user(self, user: User):
        await asyncio.to_thread(firebase.save_user, user)

    async def load_user(self, user_id: int) -> User | None:
        return await asyncio.to_thread(firebase.load_user, user_id)

    async def update_user_fields(self, user_id: int, fields: dict) -> None:
        await asyncio.to_thread(firebase.update_user_fields, user_id, fields)

    async def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        return await asyncio.to_thread(firebase.load_user_fields, user_id, fields)
