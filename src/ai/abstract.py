# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext

from abc import ABC, abstractmethod


class AIModel(ABC):

    NAME = "AI"
    TOKEN_URL = "https://google.com :)"

    @staticmethod
    def clean_token(token: str) -> str | None:
        token = token.strip()
        return token if token else None

    @abstractmethod
    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:
        pass
