# -*- coding: utf-8 -*-

import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from redis.asyncio import Redis

import storage.abstract
from config import redis
from models import AISetup, Work  # , FileType
from resolvers import Resolver
from secret import secret

# from functools import partial


if __name__ == "__main__":

    bot = Bot(token=secret.TOKEN)

    global_storage = storage.abstract.FirebaseStorage()
    resolvers = Resolver(storage_manager=global_storage)

    local_storage = RedisStorage(
        redis=Redis(**redis.settings.redis.model_dump()),
        key_builder=DefaultKeyBuilder(**redis.settings.key_builder.model_dump()),
    )

    dp = Dispatcher(storage=local_storage)

    # ** Обробники команд **
    dp.message.register(resolvers.start, Command("start"))
    dp.message.register(resolvers.setup_ai_start, Command("setup"))
    dp.message.register(resolvers.setup_ai_set_model, Command("model"))
    dp.message.register(resolvers.check_status, Command("status"))
    dp.message.register(resolvers.menu, Command("menu"))
    dp.message.register(resolvers.help, Command("help"))

    # ** Обробники інлайн-кнопок **
    dp.callback_query.register(resolvers.set_model, F.data.startswith("set_model:"))

    # ** Обробники статусів **
    dp.message.register(resolvers.setup_ai_set_token, AISetup.waiting_for_token, F.text)
    dp.message.register(
        resolvers.setup_ai_set_prompt, AISetup.waiting_for_prompt, F.text
    )
    #
    dp.message.register(resolvers.query, Work.ready, F.text)

    # ** Обробник за замовчуванням **
    dp.message.register(resolvers.default_text, F.text)

    #
    #
    # ** Інші обробники **
    # dp.message.register(
    #     partial(resolvers.media_sever, filetype=FileType.PHOTO), F.photo
    # )
    # dp.message.register(
    #     partial(resolvers.media_sever, filetype=FileType.VIDEO), F.video
    # )
    # dp.message.register(
    #     partial(resolvers.media_sever, filetype=FileType.VIDEO_NOTE), F.video_note
    # )
    # dp.message.register(
    #     partial(resolvers.media_sever, filetype=FileType.AUDIO), F.audio
    # )
    # dp.message.register(
    #     partial(resolvers.media_sever, filetype=FileType.VOICE), F.voice
    # )
    # dp.message.register(
    #     partial(resolvers.media_sever, filetype=FileType.DOCUMENT), F.document
    # )
    #
    # dp.message.register(resolvers.sticker, F.sticker)
    # dp.message.register(resolvers.contact, F.contact)
    # dp.message.register(resolvers.location, F.location)
    # dp.message.register(resolvers.animation, F.animation)

    dp.message.register(resolvers.other)

    # запускаємо обробку вхідних повідомлень
    asyncio.run(dp.start_polling(bot))
