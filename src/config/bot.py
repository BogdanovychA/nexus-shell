# -*- coding: utf-8 -*-

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from models import GlobalStorage


class BotSettings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    default_locale: str = "en"

    global_storage: GlobalStorage | None = None

    model_config = SettingsConfigDict(
        env_file=base_dir / ".env",
        env_prefix="MAIN__",
        extra="ignore",
    )


settings = BotSettings()
