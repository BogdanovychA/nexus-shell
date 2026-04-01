# -*- coding: utf-8 -*-

from pymongo import MongoClient

from config import mongo
from models import User
from utils import utils

client = MongoClient(mongo.settings.url)
db = client[mongo.settings.db]
users = db[mongo.settings.main_collection]


def save_user(user: User) -> None:
    """Збереження користувача у MongoDB"""

    data = user.model_dump()
    update_user_fields(user.id, data)


def update_user_fields(user_id: int, fields: dict) -> None:
    """Оновлення даних користувача у MongoDB"""

    fields = utils.flatten_dict(fields)

    fields.pop("_id", None)
    fields.pop("id", None)

    if not fields:
        return

    users.update_one({"_id": user_id}, {"$set": fields}, upsert=True)


def load_user_fields(user_id: int, fields: set[str] | None = None) -> dict | None:
    """Завантаження даних користувача з MongoDB"""

    if fields or fields is None:
        projection = {f: 1 for f in fields} if fields else None
    else:
        return {}

    raw_data = users.find_one({"_id": user_id}, projection)

    if not raw_data:
        return None

    data = dict(raw_data)
    data.pop("_id", None)

    return data


def load_user(user_id: int) -> User | None:
    """Завантаження користувача з MongoDB"""

    return utils.load_user(user_id, load_user_fields)
