# -*- coding: utf-8 -*-
import logging
from unittest.mock import MagicMock

import pytest

from ai.chat_gpt import ChatGPT
from ai.claude import Claude
from ai.gemini import Gemini


@pytest.fixture
def mock_i18n():
    mock = MagicMock()
    mock.get.side_effect = lambda key, **kwargs: key
    return mock


@pytest.fixture(autouse=True)
def mute_logging():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client_class, token, expected_error",
    [
        (Gemini, "", "error-no-token"),
        (Gemini, "   ", "error-no-token"),
        (Gemini, "bad token", "error-invalid-token"),
        (Gemini, "кирилиця в токені", "error-invalid-token"),
        (ChatGPT, "", "error-no-token"),
        (ChatGPT, "   ", "error-no-token"),
        (ChatGPT, "bad token", "error-invalid-token"),
        (ChatGPT, "кирилиця в токені", "error-forbidden-chars"),
        (Claude, "", "error-no-token"),
        (Claude, "   ", "error-no-token"),
        (Claude, "bad token", "error-invalid-token"),
        (Claude, "кирилиця в токені", "error-forbidden-chars"),
    ],
)
async def test_ai_queries(client_class, token, expected_error, mock_i18n):

    client = client_class()

    result = await client.query(
        i18n=mock_i18n,
        token=token,
        global_prompt="test",
        local_prompt="test",
    )

    assert result == expected_error
