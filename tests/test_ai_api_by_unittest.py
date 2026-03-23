# -*- coding: utf-8 -*-

import logging
import unittest
from unittest.mock import MagicMock

from ai.chat_gpt import ChatGPT
from ai.claude import Claude
from ai.gemini import Gemini


class APITest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_i18n = MagicMock()
        self.mock_i18n.get.side_effect = lambda key, **kwargs: key

        logging.disable(logging.CRITICAL)

    def tearDown(self):
        self.mock_i18n = None
        self.client = None

    async def test_gemini(self):

        cases = [
            ("", "error-no-token"),
            ("   ", "error-no-token"),
            ("bad-token", "error-invalid-token"),
            ("кирилиця в токені", "error-invalid-token"),
        ]

        self.client = Gemini()

        for token, error_msg in cases:

            with self.subTest(token=token, error_msg=error_msg):

                self.assertEqual(
                    await self.client.query(
                        i18n=self.mock_i18n,
                        token=token,
                        global_prompt="test",
                        local_prompt="test",
                    ),
                    error_msg,
                )

    async def test_chatgpt(self):

        cases = [
            ("", "error-no-token"),
            ("   ", "error-no-token"),
            ("bad-token", "error-invalid-token"),
            ("кирилиця в токені", "error-forbidden-chars"),
        ]

        self.client = ChatGPT()

        for token, error_msg in cases:

            with self.subTest(token=token, error_msg=error_msg):

                self.assertEqual(
                    await self.client.query(
                        i18n=self.mock_i18n,
                        token=token,
                        global_prompt="test",
                        local_prompt="test",
                    ),
                    error_msg,
                )

    async def test_claude(self):

        cases = [
            ("", "error-no-token"),
            ("   ", "error-no-token"),
            ("bad-token", "error-invalid-token"),
            ("кирилиця в токені", "error-forbidden-chars"),
        ]

        self.client = Claude()

        for token, error_msg in cases:

            with self.subTest(token=token, error_msg=error_msg):

                self.assertEqual(
                    await self.client.query(
                        i18n=self.mock_i18n,
                        token=token,
                        global_prompt="test",
                        local_prompt="test",
                    ),
                    error_msg,
                )
