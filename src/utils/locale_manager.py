# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram_i18n.managers import BaseManager

from config import bot

if TYPE_CHECKING:
    from typing import Optional

    from aiogram.fsm.context import FSMContext
    from aiogram.types import User

    import storage.abstract


LANGUAGES = ["uk", "en", "pl"]


class LocaleManager(BaseManager):

    KEY = "language_code"

    def __init__(self, default_locale: str | None = None) -> None:
        super().__init__(default_locale or bot.settings.default_locale)

    async def set_locale(
        self,
        locale,
        event_from_user: Optional[User],
        state: FSMContext,
        storage_manager: storage.abstract.StorageManager,
        cache_only: bool = False,
    ) -> None:

        data = {self.KEY: locale}

        # Запис локалі в кеш
        await state.update_data(**data)

        if cache_only:
            return

        # Запис локалі в БД
        await storage_manager.update_user_data(event_from_user.id, data)

    async def get_locale_from_database(
        self,
        event_from_user: Optional[User],
        storage_manager: storage.abstract.StorageManager,
    ) -> str:

        data = await storage_manager.load_user_fields(event_from_user.id, {self.KEY})

        if data:
            locale = data[self.KEY] if self.KEY in data else ""
        else:
            locale = ""

        return locale if locale in LANGUAGES else self.default_locale

    async def get_locale(
        self,
        event_from_user: Optional[User],
        state: FSMContext,
        storage_manager: storage.abstract.StorageManager,
    ) -> str:

        locale = await state.get_value(self.KEY, default=None)

        if locale is None:
            locale = await self.get_locale_from_database(
                event_from_user, storage_manager
            )
            await self.set_locale(
                locale, event_from_user, state, storage_manager, cache_only=True
            )

        return locale if locale in LANGUAGES else self.default_locale
