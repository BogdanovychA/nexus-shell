# -*- coding: utf-8 -*-

from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

from configs.firebase_config import (
    FIREBASE_CERTIFICATE_DIRECTORY,
    FIREBASE_CERTIFICATE_FILENAME,
    FIREBASE_LIMIT,
    FIREBASE_MAIN_COLLECTION,
)
from models import User

BASE_DIR = Path(__file__).resolve().parent.parent
FIREBASE_CERTIFICATE_PATH = (
    BASE_DIR / FIREBASE_CERTIFICATE_DIRECTORY / FIREBASE_CERTIFICATE_FILENAME
)

try:
    app = firebase_admin.get_app()  # якщо вже ініціалізовано — отримуємо
except ValueError:
    cred = credentials.Certificate(FIREBASE_CERTIFICATE_PATH)
    app = firebase_admin.initialize_app(cred)  # ініціалізуємо лише один раз

db = firestore.client(app)  # після цього можна створювати клієнти сервісів

DB = db.collection(FIREBASE_MAIN_COLLECTION)


def save_user(user: User) -> None:
    """Збереження користувача у Firebase Firestore"""

    data = user.model_dump()
    DB.document(str(user.id)).set(data, merge=True)


def update_user_fields(user_id: int, fields: dict) -> None:
    """Оновлення даних користувача у Firebase Firestore"""

    DB.document(str(user_id)).set(fields, merge=True)


def load_user_fields(user_id: int, fields: set[str] | None = None) -> dict | None:
    """Завантаження даних користувача з Firebase Firestore"""

    doc_ref = DB.document(str(user_id))

    doc = doc_ref.get(field_paths=fields) if fields else doc_ref.get()

    return doc.to_dict() if doc.exists else None


def load_user(user_id: int) -> User | None:
    """Завантаження користувача з Firebase Firestore"""

    data = load_user_fields(user_id)

    if not data:
        return None

    data["id"] = user_id
    return User(**data)


def get_users(limit: int = FIREBASE_LIMIT, last_doc=None) -> list[User]:
    """Отримуємо всіх користувачів з Firebase Firestore"""

    users_list = []

    query = DB.order_by("__name__").limit(limit)

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
        users_list += get_users(limit, docs[-1])

    return users_list


if __name__ == "__main__":
    update_user_fields(125171, {"gemini": {"token1": None, "token2": "2223"}})
    print(load_user_fields(125171, fields={"token", "gemini"}))
    print(load_user(125171))
