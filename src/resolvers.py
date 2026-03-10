# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

from config import bot
from utils import constants, encryption  # , utils

# from models import FileType
# from config import telegram


if TYPE_CHECKING:
    import storage.abstract

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


async def get_model(message: Message, state: FSMContext) -> AIModels | None:

    model = await state.get_value("model", default=AIModels.NONE)

    if model == AIModels.NONE:
        await message.answer("Робоча модель не визначена.\nОбери: /model")
        return None

    if model not in AIModels:
        await message.answer(f"Поки я не вмію працювати з {model}")
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

    await message.answer(f"Налаштування для {model} збережено")


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
):

    await save_user(message, storage_manager)
    # await state.set_state(None)
    await state.clear()
    await state.update_data(model=AIModels.NONE)

    if LOGO_PATH.exists():
        await message.answer_photo(
            photo=FSInputFile(LOGO_PATH), caption=constants.START_TEXT
        )
    else:
        await message.answer(constants.START_TEXT)


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(constants.HELP_TEXT)


@router.message(Command("model"))
async def setup_ai_set_model(message: Message):

    await message.answer("Обери мовну модель:", reply_markup=_create_model_buttons())


@router.message(Command("status"))
async def check_status(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
    user_id: int | None = None,
):
    model = await get_model(message, state)
    if model is None:
        # await message.answer("Модель не обрана.\nОбери: /model")
        return

    await message.answer(f"Поточна модель: {model}")

    if user_id is None:
        user_id = message.from_user.id

    model_data = await storage_manager.load_user_fields(user_id, {model})

    if not model_data:
        await message.answer("Модель не налаштована.\nНалаштуй: /setup")
        return

    encrypted_token = model_data[model]["token"] if "token" in model_data[model] else ""

    token = encryption.decrypt(encrypted_token)

    if token is None:
        await message.answer(
            f"Помилка при дешифруванні токена для {model}. Налаштуй заново: /setup"
        )
        return

    text = (
        f"API-ключ (токен) {model}:\n{token}"
        if token
        else f"API-ключ (токен) {model} не налаштований.\nНалаштуй: /setup"
    )
    await message.answer(text)

    prompt = model_data[model]["prompt"] if "prompt" in model_data[model] else ""
    text = (
        f"Генеральний промпт {model}:\n\n{prompt}"
        if prompt
        else f"Генеральний промпт {model} не налаштований.\nНалаштуй: /setup"
    )
    await message.answer(text)

    if token and prompt:
        await state.update_data(token=token, prompt=prompt)
        await message.answer(f"Можна працювати з {model}")
        await state.set_state(Work.ready)


@router.message(Command("setup"))
async def setup_ai_start(message: Message, state: FSMContext):
    await state.set_state(AISetup.waiting_for_model)
    await message.answer("Обери мовну модель:", reply_markup=_create_model_buttons())


# ** Обробники інлайн-кнопок **
@router.callback_query(F.data.startswith("set_model:"))
async def set_model(
    callback: CallbackQuery,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
):

    await callback.answer()  # Прибираємо "годинник" завантаження на кнопці

    model = callback.data.split(":")[1]

    await state.update_data(model=model)

    await callback.message.edit_text(f"✅ Модель встановлено: {model}")

    # Якщо це не прямий виклик, а ланцюжок налаштування бота через /setup
    if await state.get_state() == AISetup.waiting_for_model:
        await state.set_state(AISetup.waiting_for_token)
        await callback.message.answer(f"Введи API-ключ (токен) для {model}")
    else:  # Якщо це прямий виклик
        await check_status(
            callback.message, state, storage_manager, user_id=callback.from_user.id
        )


# ** Обробники статусів **
@router.message(AISetup.waiting_for_token, F.text)
async def setup_ai_set_token(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
):

    model = await get_model(message, state)

    if model is None:
        await state.set_state(None)
        return

    await save_ai_settings(message, state, storage_manager, model, "token")

    await message.answer("Введи генеральний промпт")
    await state.set_state(AISetup.waiting_for_prompt)


@router.message(AISetup.waiting_for_prompt, F.text)
async def setup_ai_set_prompt(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
):

    model = await get_model(message, state)

    if model is None:
        await state.set_state(None)
        return

    await save_ai_settings(message, state, storage_manager, model, "prompt")

    await message.answer(f"Можна працювати з {model}")
    await state.set_state(Work.ready)


# ** Обробник запитів **
@router.message(Work.ready, F.text)
async def query(
    message: Message,
    state: FSMContext,
    storage_manager: storage.abstract.StorageManager,
):

    model = await get_model(message, state)
    if model is None:
        await message.answer(f"Щось пішло не так. Налаштуй бота: /setup")
        return

    clients = {
        AIModels.GEMINI: ai.abstract.Gemini,
        AIModels.GPT: ai.abstract.ChatGPT,
        AIModels.CLAUDE: ai.abstract.Claude,
    }

    client_class = clients.get(model)
    if not client_class:
        await message.answer(f"Я поки не вмію працювати з {model}.\nОбери іншу: /model")
        return

    client = client_class()

    await message.answer(f"Зчитую API-ключ та генеральний промпт...")

    data = await state.get_data()
    token = data.get("token")
    prompt = data.get("prompt")

    if token is None or prompt is None:  # Перестраховка :)
        await message.answer(f"Налаштування в кеші не знайдено. Читаю базу даних...")
        await message.answer(f"Завантажую API-ключ та генеральний промпт...")

        model_data = await storage_manager.load_user_fields(
            message.from_user.id, {model}
        )

        encrypted_token = model_data[model]["token"]
        token = encryption.decrypt(encrypted_token)

        prompt = model_data[model]["prompt"]

        if not token or not prompt:
            await message.answer(f"Модель {model} не налаштована.\nНалаштуй: /setup")
            await state.set_state(None)
            return

        await state.update_data(token=token, prompt=prompt)

    answer_message = await message.answer(
        f"⏳ Звертаюся до {model}... Запит може тривати до 2-3 хвилин..."
    )

    text = await client.query(
        token=token, global_prompt=prompt, local_prompt=message.text
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
                file, caption="Відповідь занадто довга. Надсилаю файлом."
            )
        else:
            logger.exception("TelegramBadRequest unexpected error")
            file = BufferedInputFile(
                error_message.encode("utf-8"), filename="error.txt"
            )
            await message.answer_document(
                file,
                caption=f"Непередбачувана помилка при зверненні до {model}. {constants.FORWARD_TEXT}",
            )


# ** Обробник за замовчуванням **
@router.message(F.text)
async def default_text(message: Message):
    await message.answer(
        "Перед тим, як звертатися до мовної моделі, перевір свої налаштування: /status"
    )


# # ** Обробник медіафайлів **
# @router.message(F.photo | F.video | F.video_note | F.audio | F.voice | F.document)
# async def media_server(message: Message, bot: Bot):
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
#         await message.answer("Ви не адмін :(")
#         return
#
#     await utils.save_file(message, bot, filetype, base_path=DOWNLOAD_PATH)


# ** Сміттєприймач :) **
@router.message()
async def other(message: Message):
    await message.answer("Я працюю лише з текстовими повідомленнями")
