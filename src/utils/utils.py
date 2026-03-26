# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from aiogram.types import Message

from models import FileType

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
