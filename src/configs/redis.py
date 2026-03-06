# -*- coding: utf-8 -*-

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    """Налаштування суто для підключення до Redis"""

    host: str
    port: int
    username: str
    password: str
    db: int
    decode_responses: bool = True


class KeyBuilderSettings(BaseSettings):
    """Налаштування для DefaultKeyBuilder"""

    with_bot_id: bool = True
    prefix: str


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):

    redis: RedisSettings | None = None
    key_builder: KeyBuilderSettings | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_nested_delimiter="__"
    )


settings = Settings()
