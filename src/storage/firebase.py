# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

from models import User


class FirebaseManager:
    def __init__(self, fb_key_path: Path, collection: str, limit: int) -> None:

        try:
            self.app = firebase_admin.get_app()  # якщо вже ініціалізовано — отримуємо
        except ValueError:
            self.cred = credentials.Certificate(fb_key_path)
            self.app = firebase_admin.initialize_app(
                self.cred
            )  # ініціалізуємо лише один раз

        self.db = firestore.client(
            self.app
        )  # після цього можна створювати клієнти сервісів
        self.DB = self.db.collection(collection)

        self.limit = limit

    def save_user(self, user: User) -> None:
        """Збереження користувача у Firebase Firestore"""

        data = user.model_dump()
        self.DB.document(str(user.id)).set(data, merge=True)

    def update_user_fields(self, user_id: int, fields: dict) -> None:
        """Оновлення даних користувача у Firebase Firestore"""

        self.DB.document(str(user_id)).set(fields, merge=True)

    def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        """Завантаження даних користувача з Firebase Firestore"""

        doc_ref = self.DB.document(str(user_id))

        doc = doc_ref.get(field_paths=fields) if fields else doc_ref.get()

        return doc.to_dict() if doc.exists else None

    def get_users(self, limit: int | None = None, last_doc=None) -> list[User]:
        """Отримуємо всіх користувачів з Firebase Firestore"""

        if not limit:
            limit = self.limit

        users_list = []

        query = self.DB.order_by("__name__").limit(limit)

        if last_doc is not None:
            query = query.start_after(last_doc)

        docs = list(
            query.get()
        )  # .get() повертає не звичайний список, тому конвертуємо його

        for doc in docs:
            data = doc.to_dict()
            user = User(**data)
            users_list.append(user)

        if len(docs) == limit:
            users_list += self.get_users(limit, docs[-1])

        return users_list
