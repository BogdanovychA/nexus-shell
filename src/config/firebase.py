# -*- coding: utf-8 -*-

from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent


class FirebaseConfig(BaseModel):
    path: str = BASE_DIR / "secret" / "firebase-admin_sdk.json"
    main_collection: str = "users"
    limit: int = 100


settings = FirebaseConfig()
