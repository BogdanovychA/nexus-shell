# -*- coding: utf-8 -*-

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from redis.asyncio import Redis

import storage.abstract
from config import bot, redis, telegram
from resolvers import router


async def set_main_menu(the_bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="Запустити бота"),
        BotCommand(command="/setup", description="Швидкий старт"),
        BotCommand(command="/model", description="Змінити мовну модель"),
        BotCommand(command="/status", description="Перевірити поточні налаштування"),
        BotCommand(command="/help", description="Допомога з отриманням API-ключів"),
    ]
    await the_bot.set_my_commands(main_menu_commands, scope=BotCommandScopeDefault())


async def main():
    telegram_bot = Bot(token=telegram.settings.token)

    # # Не відповідати на повідомлення, що надійшли, поки бот був вимкнений
    # await telegram_bot.delete_webhook(drop_pending_updates=True)

    await set_main_menu(telegram_bot)

    local_storage = RedisStorage(
        redis=Redis(**redis.settings.redis.model_dump()),
        key_builder=DefaultKeyBuilder(**redis.settings.key_builder.model_dump()),
    )

    global_storage = storage.abstract.FirebaseStorage()

    dp = Dispatcher(storage=local_storage, storage_manager=global_storage)

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path=bot.settings.base_dir / "locales" / "{locale}"),
        default_locale="uk",
    )

    i18n_middleware.setup(dp)

    dp.include_router(router)

    await dp.start_polling(telegram_bot)


if __name__ == "__main__":
    asyncio.run(main())
