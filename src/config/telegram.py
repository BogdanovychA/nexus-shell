# -*- coding: utf-8 -*-

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class TelegramSettings(BaseSettings):
    token: str | None = None
    admin_id: int | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_prefix="TELEGRAM__", extra="ignore"
    )


settings = TelegramSettings()
