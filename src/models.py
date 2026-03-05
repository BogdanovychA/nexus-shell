# -*- coding: utf-8 -*-

from enum import StrEnum

from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel, ConfigDict


class User(BaseModel):

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_premium: bool | None = None
    is_bot: bool | None = None
    language_code: str | None = None


class FileType(StrEnum):
    VIDEO = "video"
    AUDIO = "audio"
    VIDEO_NOTE = "video_note"
    PHOTO = "photo"
    DOCUMENT = "document"
    VOICE = "voice"


class AISetup(StatesGroup):

    waiting_for_model = State()
    waiting_for_token = State()
    waiting_for_prompt = State()


class Work(StatesGroup):
    ready = State()
    not_ready = State()


class AIModels(StrEnum):
    NONE = "None"
    GEMINI = "Gemini"
    GPT = "ChatGPT"
    CLAUDE = "Claude"
