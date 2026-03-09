# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import FSInputFile

from config import bot
from utils import constants

if TYPE_CHECKING:
    import storage.abstract

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


class Resolver:

    BASE_PATH = bot.settings.base_dir / "downloads"
    LOGO_PATH = bot.settings.base_dir / "src" / "assets" / "images" / "logo.jpg"

    def __init__(self, storage_manager: storage.abstract.StorageManager):
        self.storage_manager = storage_manager

    def save_user(self, message: Message) -> None:

        user = User.model_validate(message.from_user)
        self.storage_manager.save_user(user)

    @staticmethod
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
        self, message: Message, state: FSMContext, model: AIModels, key: str
    ) -> None:

        value = message.text
        data = {model: {key: value}}

        self.storage_manager.update_user_fields(message.from_user.id, data)
        await state.update_data(key=value)

        await message.answer(f"Налаштування для {model} збережено")

    async def start(self, message: Message, state: FSMContext):

        self.save_user(message)
        # await state.set_state(None)
        await state.clear()
        await state.update_data(model=AIModels.NONE)

        if self.LOGO_PATH.exists():
            await message.answer_photo(
                photo=FSInputFile(self.LOGO_PATH), caption=constants.START_TEXT
            )
        else:
            await message.answer(constants.START_TEXT)

    @staticmethod
    async def menu(message: Message):
        await message.answer(constants.MENU_TEXT)

    @staticmethod
    async def help(message: Message):
        await message.answer(constants.HELP_TEXT)

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

    async def set_model(self, callback: CallbackQuery, state: FSMContext):

        await callback.answer()  # Прибираємо "годинник" завантаження на кнопці

        model = callback.data.split(":")[1]

        await state.update_data(model=model)

        await callback.message.edit_text(f"✅ Модель встановлено: {model}")

        # Якщо це не прямий виклик, а ланцюжок налаштування бота через /setup
        if await state.get_state() == AISetup.waiting_for_model:
            await state.set_state(AISetup.waiting_for_token)
            await callback.message.answer(f"Введи API-ключ (токен) для {model}")
        else:  # Якщо це прямий виклик
            await self.check_status(
                callback.message, state, user_id=callback.from_user.id
            )

    async def check_status(
        self, message: Message, state: FSMContext, user_id: int | None = None
    ):
        model = await self.get_model(message, state)
        if model is None:
            # await message.answer("Модель не обрана.\nОбери: /model")
            return

        await message.answer(f"Поточна модель: {model}")

        if user_id is None:
            user_id = message.from_user.id

        model_data = self.storage_manager.load_user_fields(user_id, {model})

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
            else f"Генеральний промпт {model} не налаштований.\nНалаштуй: /setup"
        )
        await message.answer(text)

        if token and prompt:
            await state.update_data(token=token, prompt=prompt)
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

        await self.save_ai_settings(message, state, model, "token")

        await message.answer("Введи генеральний промпт")
        await state.set_state(AISetup.waiting_for_prompt)

    async def setup_ai_set_prompt(self, message: Message, state: FSMContext):

        model = await self.get_model(message, state)

        if model is None:
            await state.set_state(None)
            return

        await self.save_ai_settings(message, state, model, "prompt")

        await message.answer(f"Можна працювати з {model}")
        await state.set_state(Work.ready)

    async def query(self, message: Message, state: FSMContext):

        model = await self.get_model(message, state)
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
            await message.answer(
                f"Я поки не вмію працювати з {model}.\nОбери іншу: /model"
            )
            return

        client = client_class()

        await message.answer(f"Зчитую API-ключ та генеральний промпт...")

        data = await state.get_data()
        token = data.get("token")
        prompt = data.get("prompt")

        if token is None or prompt is None:  # Перестраховка :)
            await message.answer(
                f"Налаштування в кеші не знайдено. Читаю базу даних..."
            )
            await message.answer(f"Завантажую API-ключ та генеральний промпт...")

            model_data = self.storage_manager.load_user_fields(
                message.from_user.id, {model}
            )

            token = model_data[model]["token"]
            prompt = model_data[model]["prompt"]

            if not token or not prompt:
                await message.answer(
                    f"Модель {model} не налаштована.\nНалаштуй: /setup"
                )
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
            if (
                "too long" in error_message.lower()
                or "too_long" in error_message.lower()
            ):
                file = BufferedInputFile(text.encode("utf-8"), filename="result.txt")
                await message.answer_document(
                    file, caption="Відповідь занадто довга. Надсилаю файлом."
                )
            else:
                file = BufferedInputFile(
                    error_message.encode("utf-8"), filename="error.txt"
                )
                await message.answer_document(
                    file,
                    caption=f"Непередбачувана помилка при зверненні до {model}. {constants.FORWARD_TEXT}",
                )
                print(error_message)

    @staticmethod
    async def default_text(message: Message):
        await message.answer(
            "Перед тим, як звертатися до мовної моделі, перевір свої налаштування: /status"
        )

    # async def media_sever(self, message: Message, bot: Bot, filetype: FileType):
    #
    #     if message.from_user.id == telegram.settings.admin_id:
    #         await utils.save_file(message, bot, filetype, base_path=self.BASE_PATH)
    #     else:
    #         await message.answer("Ви не адмін :(")

    @staticmethod
    async def other(message: Message):
        await message.answer("Я працюю лише з текстовими повідомленнями")
