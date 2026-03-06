# -*- coding: utf-8 -*-

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from storage import firebase

if TYPE_CHECKING:
    from models import User


class StorageManager(ABC):

    @abstractmethod
    def save_user(self, user: User):
        """Збереження користувача в БД"""
        pass

    @abstractmethod
    def load_user(self, user_id: int) -> User | None:
        """Завантаження користувача з БД"""
        pass

    @abstractmethod
    def update_user_fields(self, user_id: int, fields: dict) -> None:
        """Оновлення даних користувача"""
        pass

    @abstractmethod
    def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        """Завантаження даних користувача"""
        pass


class FirebaseStorage(StorageManager):

    def save_user(self, user: User):
        firebase.save_user(user)

    def load_user(self, user_id: int) -> User | None:
        return firebase.load_user(user_id)

    def update_user_fields(self, user_id: int, fields: dict) -> None:
        firebase.update_user_fields(user_id, fields)

    def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        return firebase.load_user_fields(user_id, fields)
