# -*- coding: utf-8 -*-


import logging

from cryptography.fernet import Fernet, InvalidToken

from config import encryption

logger = logging.getLogger(__name__)


_cipher = Fernet(encryption.settings.secret_key.encode())


def encrypt(text: str) -> str:
    return _cipher.encrypt(text.encode()).decode()


def decrypt(text: str) -> str | None:
    try:
        return _cipher.decrypt(text.encode()).decode()
    except InvalidToken:
        logger.warning("Failed to decrypt token — invalid or corrupted data")
        return None
