# -*- coding: utf-8 -*-

from pymongo import MongoClient

from models import User
from utils import utils


class MongoManager:

    def __init__(self, url: str, database: str, collection: str) -> None:
        self.client = MongoClient(url)
        self.db = self.client[database]
        self.users = self.db[collection]

    def save_user(self, user: User) -> None:
        """Збереження користувача у MongoDB"""

        data = user.model_dump()
        self.update_user_fields(user.id, data)

    def update_user_fields(self, user_id: int, fields: dict) -> None:
        """Оновлення даних користувача у MongoDB"""

        fields = utils.flatten_dict(fields)

        fields.pop("_id", None)
        fields.pop("id", None)

        if not fields:
            return

        self.users.update_one({"_id": user_id}, {"$set": fields}, upsert=True)

    def load_user_fields(
        self, user_id: int, fields: set[str] | None = None
    ) -> dict | None:
        """Завантаження даних користувача з MongoDB"""

        if fields or fields is None:
            projection = {f: 1 for f in fields} if fields else None
        else:
            return {}

        raw_data = self.users.find_one({"_id": user_id}, projection)

        if not raw_data:
            return None

        data = dict(raw_data)
        data.pop("_id", None)

        return data
