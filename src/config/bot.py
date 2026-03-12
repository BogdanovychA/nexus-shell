# -*- coding: utf-8 -*-

from pathlib import Path

from pydantic import BaseModel


class BotSettings(BaseModel):
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    default_locale: str = "en"


settings = BotSettings()
