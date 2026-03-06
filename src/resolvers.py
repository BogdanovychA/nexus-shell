# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import FSInputFile

if TYPE_CHECKING:
    from models import FileType
    import storage.abstract

from pathlib import Path

from aiogram import Bot
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
from configs.config import ADMIN_ID
from models import AIModels, AISetup, User, Work
from utils import utils

BASE_DIR = Path(__file__).resolve().parent.parent


class Resolver:

    BASE_PATH = BASE_DIR / "downloads"

    START_TEXT = (
        "🤖 Привіт! Мене звати Nexus Shell | AI Agent\n\n"
        "Ти підключився до універсальної оболонки для роботи з провідними мовними моделями. "
        "Тепер Gemini, GPT та Claude доступні в одному інтерфейсі твого Telegram.\n\n"
        "Щоб розпочати роботу, виконай три прості кроки:\n\n"
        "1️⃣ 🔑 Підключи API-ключ\n"
        "Скористайся командою `/setup`, щоб додати свій ключ від потрібної моделі. "
        "Я підтримую пряму інтеграцію, що забезпечує швидкість та конфіденційність.\n\n"
        "2️⃣ 🧠 Встанови Генеральний промпт\n"
        "Задай контекст, роль або правила поведінки свого агента. Це дозволить боту "
        "стати асистентом, аналітиком або розробником.\n\n"
        "3️⃣ 🚀 Починай роботу\n"
        "Надсилай звичайні промпти, і твій кастомний агент миттєво візьметься до виконання завдань.\n\n"
        "--- \n"
        "Використовуй /menu або /help, щоб дізнатися про всі можливості."
    )

    MENU_TEXT = (
        "Натисни:\n\n"
        + "🔹 /setup для швидкого старту\n\n"
        + "🔹 /model щоб обрати мовну модель\n\n"
        + "🔹 /status щоб перевірити налаштування\n\n"
        + "🔹 /help щоб дізнатися, де взяти API-ключ (токен) від мовної моделі\n\n"
        + "🔹 /menu щоб переглянути це меню ще раз\n\n"
    )

    HELP_TEXT = (
        "🔑 Де отримати API-ключі для Nexus Shell?\n\n"
        "Для роботи бота тобі необхідно згенерувати ключі на офіційних платформах розробників:\n\n"
        "🔹 Gemini (Google):\n"
        f"{ai.abstract.GEMINI_URL}\n\n"
        "🔹 Claude (Anthropic):\n"
        f"{ai.abstract.CLAUDE_URL}\n\n"
        "🔹 ChatGPT (OpenAI):\n"
        f"{ai.abstract.CHATGPT_URL}\n\n"
        "--- \n"
        "⚠️ Важливо:\n"
        "• Ключі використовуються виключно для запитів до моделей.\n"
        "• Переконайся, що на балансі (Google/Anthropic/OpenAI) є кошти для оплати запитів через API.\n\n"
    )

    def __init__(self, storage_manager: storage.abstract.StorageManager):
        self.storage_manager = storage_manager

    def save_user(self, message: Message) -> None:

        user = User.model_validate(message.from_user)
        self.storage_manager.save_user(user)

    @staticmethod
    async def get_model(message: Message, state: FSMContext) -> AIModels | None:

        model = await state.get_value("model", default=AIModels.NONE)

        if model == AIModels.NONE:  # Необхідно допрацювати
            await message.answer("Робоча модель не визначена.\nОбери: /model")
            return None

        if model not in AIModels:  # Необхідно допрацювати
            await message.answer(f"Поки я не вмію працювати з {model}")
            return None

        return model

    async def save_ai_settings(
        self, message: Message, model: AIModels, key: str
    ) -> None:

        value = message.text
        data = {model: {key: value}}

        self.storage_manager.update_user_fields(message.from_user.id, data)

        await message.answer(f"Налаштування для {model} збережено")

    async def start(self, message: Message, state: FSMContext):

        self.save_user(message)
        await state.set_state(None)
        await state.update_data(model=AIModels.NONE)

        logo_path = BASE_DIR / "src" / "assets" / "images" / "logo.jpg"
        await message.answer_photo(
            photo=FSInputFile(logo_path), caption=self.START_TEXT
        )

        # await message.answer(self.START_TEXT)

    async def menu(self, message: Message):
        await message.answer(self.MENU_TEXT)

    async def help(self, message: Message):
        await message.answer(self.HELP_TEXT)

    @staticmethod
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

    async def setup_ai_set_model(self, message: Message):

        await message.answer(
            "Обери мовну модель:", reply_markup=self._create_model_buttons()
        )

    @staticmethod
    async def set_model(callback: CallbackQuery, state: FSMContext):

        model = callback.data.split(":")[1]

        await state.update_data(model=model)

        await callback.message.answer(f"Модель встановлено: {model}")

        if await state.get_state() == AISetup.waiting_for_model:
            await state.set_state(AISetup.waiting_for_token)
            await callback.message.answer(f"Введи API-ключ (токен) для {model}")

    async def check_status(self, message: Message, state: FSMContext):

        model = await self.get_model(message, state)
        if model is None:
            # await message.answer("Модель не обрана.\nОбери: /model")
            return

        await message.answer(f"Поточна модель: {model}")

        model_data = self.storage_manager.load_user_fields(
            message.from_user.id, {model}
        )

        if not model_data:
            await message.answer("Модель не налаштована.\nНалаштуй: /setup")
            return

        token = model_data[model]["token"] if "token" in model_data[model] else ""
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
            else f"Промпт {model} не налаштований.\nНалаштуй: /setup"
        )
        await message.answer(text)

        if token and prompt:
            await message.answer(f"Можна працювати з {model}")
            await state.set_state(Work.ready)

    async def setup_ai_start(self, message: Message, state: FSMContext):
        await state.set_state(AISetup.waiting_for_model)
        await message.answer(
            "Обери мовну модель:", reply_markup=self._create_model_buttons()
        )

    async def setup_ai_set_token(self, message: Message, state: FSMContext):

        model = await self.get_model(message, state)

        if model is None:
            await state.set_state(None)
            return

        await self.save_ai_settings(message, model, "token")

        await message.answer("Введи генеральний промпт")

        await state.set_state(AISetup.waiting_for_prompt)

    async def setup_ai_set_prompt(self, message: Message, state: FSMContext):

        model = await self.get_model(message, state)

        if model is None:
            await state.set_state(None)
            return

        await self.save_ai_settings(message, model, "prompt")

        await message.answer(f"Можна працювати з {model}")
        await state.set_state(Work.ready)

    async def query(self, message: Message, state):

        model = await self.get_model(message, state)
        if model is None:
            await message.answer(f"Щось пішло не так. Налаштуй бота: /setup")
            return

        match model:
            case AIModels.GEMINI:
                client = ai.abstract.Gemini()
            case AIModels.GPT:
                client = ai.abstract.ChatGPT()
            case AIModels.CLAUDE:
                client = ai.abstract.Claude()
            case _:
                await message.answer(
                    f"Я поки не вмію працювати з {model}.\nОбери іншу: /model"
                )
                return

        await message.answer(f"Завантажую API-ключ та генеральний промпт...")

        model_data = self.storage_manager.load_user_fields(
            message.from_user.id, {model}
        )

        token = model_data[model]["token"]
        global_prompt = model_data[model]["prompt"]
        local_prompt = message.text

        await message.answer(
            f"Звертаюся до {model}... Запит може тривати до 2-3 хвилин..."
        )

        text = await client.query(token, global_prompt, local_prompt)

        # Обмеження Телеграму щодо довжини
        try:
            await message.answer(text)

        except TelegramBadRequest as e:
            if "message is too long" in str(e):
                file = BufferedInputFile(text.encode("utf-8"), filename="result.txt")
                await message.answer_document(
                    file, caption="Відповідь занадто довга. Надсилаю файлом."
                )

            else:
                file = BufferedInputFile(str(e).encode("utf-8"), filename="error.txt")
                await message.answer_document(
                    file, caption=f"Непередбачувана помилка при зверненні до {model}."
                )

    @staticmethod
    async def default_text(message: Message):
        await message.answer(
            "Перед тим, як звертатися до мовної моделі, перевір свої налаштування: /status"
        )

    # async def media_sever(self, message: Message, bot: Bot, filetype: FileType):
    #
    #     if message.from_user.id == ADMIN_ID:
    #         await utils.save_file(message, bot, filetype, base_path=self.BASE_PATH)
    #     else:
    #         await message.answer("Ви не адмін :(")
    #
    # async def sticker(self, message: Message):
    #     await message.answer("sticker")
    #
    # async def contact(self, message: Message):
    #     await message.answer("contact")
    #
    # async def location(self, message: Message):
    #     await message.answer("location")
    #
    # async def animation(self, message: Message):
    #     await message.answer("animation")

    async def other(self, message: Message):
        await message.answer("Я працюю лише з текстовими повідомленнями")
