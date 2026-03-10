# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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
