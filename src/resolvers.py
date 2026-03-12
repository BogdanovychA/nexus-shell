# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

from config import bot
from utils import encryption  # , utils

# from models import FileType
# from config import telegram


if TYPE_CHECKING:
    import storage.abstract
    from aiogram_i18n import I18nContext

    # from aiogram import Bot

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import ai.abstract
from models import AIModels, AISetup, User, Work

# DOWNLOAD_PATH = bot.settings.base_dir / "downloads"
LOGO_PATH = bot.settings.base_dir / "src" / "assets" / "images" / "logo.jpg"


logger = logging.getLogger(__name__)

router = Router()


async def save_user(
    message: Message, storage_manager: storage.abstract.StorageManager
) -> None:

    user = User.model_validate(message.from_user)
    await storage_manager.save_user(user)


async def get_model(
    message: Message, state: FSMContext, i18n: I18nContext
) -> AIModels | None:

    model = await state.get_value("model", default=AIModels.NONE)

    if model == AIModels.NONE:
        await message.answer("Робоча модель не визначена.\nОбери: /model")
        return None

    if model not in AIModels:
        await message.answer(i18n.get("model-not-supported", model=model))
        return None

    return model


async def save_ai_settings(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    model: AIModels,
    key: str,
) -> None:

    value = message.text

    await state.update_data(**{key: value})  # зберігаємо оригінал у кеш (Redis)

    if key == "token":
        value = encryption.encrypt(value)  # шифруємо перед записом у БД

    data = {model: {key: value}}
    await storage_manager.update_user_fields(message.from_user.id, data)

    await message.answer("Налаштування для {model} збережено".format(model=model))


def _create_model_buttons():
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text=AIModels.GEMINI, callback_data=f"set_model:{AIModels.GEMINI}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=AIModels.GPT, callback_data=f"set_model:{AIModels.GPT}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=AIModels.CLAUDE, callback_data=f"set_model:{AIModels.CLAUDE}"
        )
    )

    builder.adjust(1)  # По одній в рядок

    return builder.as_markup()


# ** Обробники команд **
@router.message(Command("start"))
async def start_command(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    i18n: I18nContext,
):

    await save_user(message, storage_manager)
    # await state.set_state(None)
    await state.clear()
    await state.update_data(model=AIModels.NONE)

    if LOGO_PATH.exists():
        await message.answer_photo(
            photo=FSInputFile(LOGO_PATH), caption=i18n.get("info-start-text")
        )
    else:
        await message.answer(i18n.get("info-start-text"))


@router.message(Command("help"))
async def help_command(message: Message, i18n: I18nContext):
    await message.answer(i18n.get("info-help-text"))


@router.message(Command("model"))
async def setup_ai_set_model(message: Message, i18n: I18nContext):
    await message.answer(i18n.get("model-select"), reply_markup=_create_model_buttons())


@router.message(Command("status"))
async def check_status(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    i18n: I18nContext,
    user_id: int | None = None,
):
    model = await get_model(message, state, i18n)
    if model is None:
        return

    await message.answer(i18n.get("status-current-model", model=model))

    if user_id is None:
        user_id = message.from_user.id

    model_data = await storage_manager.load_user_fields(user_id, {model})

    if not model_data:
        await message.answer(i18n.get("model-not-configured", model=model))
        return

    encrypted_token = model_data[model]["token"] if "token" in model_data[model] else ""

    token = encryption.decrypt(encrypted_token)

    if token is None:
        await message.answer(i18n.get("status-decrypt-error", model=model))
        return

    text = (
        i18n.get("status-token-info", model=model, token=token)
        if token
        else i18n.get("status-token-not-set", model=model)
    )
    await message.answer(text)

    prompt = model_data[model]["prompt"] if "prompt" in model_data[model] else ""
    text = (
        i18n.get("status-prompt-info", model=model, prompt=prompt)
        if prompt
        else i18n.get("status-prompt-not-set", model=model)
    )
    await message.answer(text)

    if token and prompt:
        await state.update_data(token=token, prompt=prompt)
        await message.answer(i18n.get("setup-ready", model=model))
        await state.set_state(Work.ready)


@router.message(Command("setup"))
async def setup_ai_start(
    message: Message,
    state: FSMContext,
    i18n: I18nContext,
):
    await state.set_state(AISetup.waiting_for_model)
    await message.answer(i18n.get("model-select"), reply_markup=_create_model_buttons())


# ** Обробники інлайн-кнопок **
@router.callback_query(F.data.startswith("set_model:"))
async def set_model(
    callback: CallbackQuery,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    i18n: I18nContext,
):

    await callback.answer()  # Прибираємо "годинник" завантаження на кнопці

    model = callback.data.split(":")[1]

    await state.update_data(model=model)

    await callback.message.edit_text(i18n.get("model-set-success", model=model))

    # Якщо це не прямий виклик, а ланцюжок налаштування бота через /setup
    if await state.get_state() == AISetup.waiting_for_model:
        await state.set_state(AISetup.waiting_for_token)
        await callback.message.answer(i18n.get("setup-enter-token", model=model))
    else:  # Якщо це прямий виклик
        await check_status(
            callback.message,
            state,
            storage_manager,
            i18n,
            user_id=callback.from_user.id,
        )


# ** Обробники статусів **
@router.message(AISetup.waiting_for_token, F.text)
async def setup_ai_set_token(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    i18n: I18nContext,
):

    model = await get_model(message, state, i18n)

    if model is None:
        await state.set_state(None)
        return

    await save_ai_settings(message, state, storage_manager, model, "token")

    await message.answer(i18n.get("setup-enter-prompt"))
    await state.set_state(AISetup.waiting_for_prompt)


@router.message(AISetup.waiting_for_prompt, F.text)
async def setup_ai_set_prompt(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    i18n: I18nContext,
):

    model = await get_model(message, state, i18n)

    if model is None:
        await state.set_state(None)
        return

    await save_ai_settings(message, state, storage_manager, model, "prompt")

    await message.answer(i18n.get("setup-ready", model=model))
    await state.set_state(Work.ready)


# ** Обробник запитів **
@router.message(Work.ready, F.text)
async def query(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    i18n: I18nContext,
):

    model = await get_model(message, state, i18n)
    if model is None:
        await message.answer(i18n.get("query-some-error"))
        return

    clients = {
        AIModels.GEMINI: ai.abstract.Gemini,
        AIModels.GPT: ai.abstract.ChatGPT,
        AIModels.CLAUDE: ai.abstract.Claude,
    }

    client_class = clients.get(model)
    if not client_class:
        await message.answer(i18n.get("model-not-supported", model=model))
        return

    client = client_class()

    await message.answer(i18n.get("query-loading-config"))

    data = await state.get_data()
    token = data.get("token")
    prompt = data.get("prompt")

    if token is None or prompt is None:  # Перестраховка :)
        await message.answer(i18n.get("query-cache-missing"))
        await message.answer(i18n.get("query-loading-db"))

        model_data = await storage_manager.load_user_fields(
            message.from_user.id, {model}
        )

        encrypted_token = model_data[model]["token"]
        token = encryption.decrypt(encrypted_token)

        prompt = model_data[model]["prompt"]

        if not token or not prompt:
            await message.answer(i18n.get("model-not-configured", model=model))
            await state.set_state(None)
            return

        await state.update_data(token=token, prompt=prompt)

    answer_message = await message.answer(i18n.get("query-waiting", model=model))

    text = await client.query(
        i18n, token=token, global_prompt=prompt, local_prompt=message.text
    )

    # Обмеження Телеграму щодо довжини
    try:
        await answer_message.edit_text(text)

    except TelegramBadRequest as e:
        error_message = str(e)
        if "too long" in error_message.lower() or "too_long" in error_message.lower():
            logger.warning("TelegramBadRequest: message too long, sending as file")
            file = BufferedInputFile(text.encode("utf-8"), filename="result.txt")
            await message.answer_document(
                file, caption=i18n.get("error-telegram-too-long")
            )
        else:
            logger.exception("TelegramBadRequest unexpected error")
            file = BufferedInputFile(
                error_message.encode("utf-8"), filename="error.txt"
            )
            await message.answer_document(
                file,
                caption=f'{i18n.get("query-unexpected-error", model=model)} {i18n.get("info-forward-text")}',
            )


# ** Обробник за замовчуванням **
@router.message(F.text)
async def default_text(
    message: Message,
    i18n: I18nContext,
):
    await message.answer(i18n.get("default-text-info"))


# # ** Обробник медіафайлів **
# @router.message(F.photo | F.video | F.video_note | F.audio | F.voice | F.document)
# async def media_server(message: Message, bot: Bot, i18n: I18nContext):
#
#     if message.photo:
#         filetype = FileType.PHOTO
#     elif message.video:
#         filetype = FileType.VIDEO
#     elif message.video_note:
#         filetype = FileType.VIDEO_NOTE
#     elif message.audio:
#         filetype = FileType.AUDIO
#     elif message.voice:
#         filetype = FileType.VOICE
#     elif message.document:
#         filetype = FileType.DOCUMENT
#     else: return
#
#
#     if message.from_user.id != telegram.settings.admin_id:
#         await message.answer(i18n.get("not-admin-error"))
#         return
#
#     await utils.save_file(message, bot, filetype, base_path=DOWNLOAD_PATH)


# ** Сміттєприймач :) **
@router.message()
async def other(
    message: Message,
    i18n: I18nContext,
):
    await message.answer(i18n.get("only-text-allowed"))
