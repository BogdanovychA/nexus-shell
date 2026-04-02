# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import firebase, mongo, postgres
from storage.firebase import FirebaseManager
from storage.mongo import MongoManager
from storage.sql_alchemy.postgresql import PostgresManager

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
    async def update_user_data(self, user_id: int, fields: dict) -> None:
        """Оновлення даних користувача"""
        pass

    @abstractmethod
    async def update_ai_settings(self, user_id: int, fields: dict) -> None:
        """Оновлення Налаштувань ШІ"""
        pass

    @abstractmethod
    async def load_ai_settings(self, user_id: int, model: str) -> dict | None:
        """Завантаження Налаштувань ШІ"""
        pass

    @abstractmethod
    async def load_user_data(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        """Завантаження даних користувача"""
        pass

    @abstractmethod
    async def close(self):
        """Закриття сесії"""
        pass


class PostgresStorage(StorageManager):

    def __init__(self):
        self.engine = create_async_engine(postgres.settings.url)  # , echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.storage = PostgresManager(session_factory=self.async_session)

    async def save_user(self, user: User):
        await self.storage.save_user(user)

    async def load_user(self, user_id: int) -> User | None:
        raise NotImplementedError

    async def update_user_data(self, user_id: int, fields: dict) -> None:
        await self.storage.update_user_data(user_id, fields)

    async def update_ai_settings(self, user_id: int, fields: dict) -> None:
        await self.storage.update_ai_settings(user_id, fields)

    async def load_ai_settings(self, user_id: int, model: str) -> dict | None:
        return await self.storage.load_ai_settings(user_id, model)

    async def load_user_data(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        return await self.storage.load_user_data(user_id, fields)

    async def close(self):
        await self.engine.dispose()


class FirebaseStorage(StorageManager):

    def __init__(self):
        self.storage = FirebaseManager(
            fb_key_path=firebase.settings.path,
            collection=firebase.settings.main_collection,
            limit=firebase.settings.limit,
        )

    async def save_user(self, user: User):
        await asyncio.to_thread(self.storage.save_user, user)

    async def load_user(self, user_id: int) -> User | None:
        return await asyncio.to_thread(self.storage.load_user, user_id)

    async def update_user_data(self, user_id: int, fields: dict) -> None:
        await asyncio.to_thread(self.storage.update_user_fields, user_id, fields)

    async def update_ai_settings(self, user_id: int, fields: dict) -> None:
        await asyncio.to_thread(self.storage.update_user_fields, user_id, fields)

    async def load_ai_settings(self, user_id: int, model: str) -> dict | None:
        return await asyncio.to_thread(self.storage.load_user_fields, user_id, {model})

    async def load_user_data(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        return await asyncio.to_thread(self.storage.load_user_fields, user_id, fields)

    async def close(self):
        self.storage = None


class MongoStorage(StorageManager):

    def __init__(self):
        self.storage = MongoManager(
            url=mongo.settings.url,
            database=mongo.settings.db,
            collection=mongo.settings.main_collection,
        )

    async def save_user(self, user: User):
        await asyncio.to_thread(self.storage.save_user, user)

    async def load_user(self, user_id: int) -> User | None:
        return await asyncio.to_thread(self.storage.load_user, user_id)

    async def update_user_data(self, user_id: int, fields: dict) -> None:
        await asyncio.to_thread(self.storage.update_user_fields, user_id, fields)

    async def update_ai_settings(self, user_id: int, fields: dict) -> None:
        await asyncio.to_thread(self.storage.update_user_fields, user_id, fields)

    async def load_ai_settings(self, user_id: int, model: str) -> dict | None:
        return await asyncio.to_thread(self.storage.load_user_fields, user_id, {model})

    async def load_user_data(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        return await asyncio.to_thread(self.storage.load_user_fields, user_id, fields)

    async def close(self):
        self.storage.client.close()
