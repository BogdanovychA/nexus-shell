# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import bot


class EncryptionConfig(BaseSettings):
    secret_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=bot.settings.base_dir / ".env",
        env_prefix="CRYPTOGRAPHY__",
        extra="ignore",
    )


settings = EncryptionConfig()
