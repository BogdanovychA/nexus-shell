# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable

from aiogram.types import Message

from models import FileType, User

if TYPE_CHECKING:
    from pathlib import Path

    from aiogram import Bot


async def send_message(bot: Bot, chat_id: int, text: str):
    await bot.send_message(chat_id, text)


async def save_file(message: Message, bot: Bot, filetype: FileType, base_path: Path):
    extensions = {
        FileType.VIDEO: "mp4",
        FileType.VIDEO_NOTE: "mp4",
        FileType.AUDIO: "mp3",
        FileType.PHOTO: "jpg",
        FileType.DOCUMENT: "file",
        FileType.VOICE: "ogg",
    }

    ext = extensions.get(filetype)

    if not ext:
        return

    user_dir = base_path / filetype / str(message.from_user.id)
    await asyncio.to_thread(user_dir.mkdir, parents=True, exist_ok=True)

    media = getattr(message, filetype, None)
    if media is None:
        return

    if filetype == "photo" and isinstance(media, list):
        media = media[-1]

    if not hasattr(media, "file_id"):
        return

    try:
        file = await bot.get_file(media.file_id)

        destination = user_dir / f"{media.file_id}.{ext}"
        await bot.download_file(file.file_path, destination)

        await message.answer("Файл збережено на сервері!")

    except Exception as e:
        await message.answer(f"Помилка при збереженні файлу: {e}")


def split_text(text: str, max_length: int = 4096):
    """Розбиває текст на частини по 4096 символів."""

    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def create_user_instance(
    user_id: int, fetcher: Callable[[int], dict | None]
) -> User | None:
    """Створює об'єкт User, використовуючи надану функцію отримання даних."""

    data = fetcher(user_id)

    if not data:
        return None

    data["id"] = user_id
    return User(**data)


def flatten_dict(d: dict, parent_key: str | None = None) -> dict:
    """Перетворює вкладений словник у плоский для MongoDB Dot Notation"""

    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())  # Обережно, рекурсія! :)
        else:
            items.append((new_key, v))
    return dict(items)
