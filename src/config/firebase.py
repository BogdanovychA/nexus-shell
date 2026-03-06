# -*- coding: utf-8 -*-

from pydantic import BaseModel

from config import bot


class FirebaseConfig(BaseModel):
    path: str = bot.settings.base_dir / "src" / "secret" / "firebase-admin_sdk.json"
    main_collection: str = "users"
    limit: int = 100


settings = FirebaseConfig()
