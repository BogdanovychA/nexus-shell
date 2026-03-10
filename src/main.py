# -*- coding: utf-8 -*-

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from redis.asyncio import Redis

import storage.abstract
from config import redis, telegram
from resolvers import router


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="Запустити бота"),
        BotCommand(command="/setup", description="Швидкий старт"),
        BotCommand(command="/model", description="Змінити мовну модель"),
        BotCommand(command="/status", description="Перевірити поточні налаштування"),
        BotCommand(command="/help", description="Допомога з отриманням API-ключів"),
    ]
    await bot.set_my_commands(main_menu_commands, scope=BotCommandScopeDefault())


async def main():
    telegram_bot = Bot(token=telegram.settings.token)
    await set_main_menu(telegram_bot)

    local_storage = RedisStorage(
        redis=Redis(**redis.settings.redis.model_dump()),
        key_builder=DefaultKeyBuilder(**redis.settings.key_builder.model_dump()),
    )

    global_storage = storage.abstract.FirebaseStorage()

    dp = Dispatcher(storage=local_storage, storage_manager=global_storage)

    dp.include_router(router)

    await dp.start_polling(telegram_bot)


if __name__ == "__main__":
    asyncio.run(main())
