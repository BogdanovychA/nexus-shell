# -*- coding: utf-8 -*-


import firebase_admin
from firebase_admin import credentials, firestore

from config import firebase
from models import User
from utils import utils

try:
    app = firebase_admin.get_app()  # якщо вже ініціалізовано — отримуємо
except ValueError:
    cred = credentials.Certificate(firebase.settings.path)
    app = firebase_admin.initialize_app(cred)  # ініціалізуємо лише один раз

db = firestore.client(app)  # після цього можна створювати клієнти сервісів

DB = db.collection(firebase.settings.main_collection)


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
    return utils.load_user(user_id, load_user_fields)


def get_users(limit: int = firebase.settings.limit, last_doc=None) -> list[User]:
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
