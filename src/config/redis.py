# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import bot


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

    prefix: str
    with_bot_id: bool = True


class Settings(BaseSettings):

    redis: RedisSettings | None = None
    key_builder: KeyBuilderSettings | None = None

    model_config = SettingsConfigDict(
        env_file=bot.settings.base_dir / ".env",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
