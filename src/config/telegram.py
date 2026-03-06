# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import bot


class TelegramSettings(BaseSettings):
    token: str | None = None
    admin_id: int | None = None

    model_config = SettingsConfigDict(
        env_file=bot.settings.base_dir / ".env", env_prefix="TELEGRAM__", extra="ignore"
    )


settings = TelegramSettings()
