# -*- coding: utf-8 -*-

import logging
import unittest
from unittest.mock import MagicMock

from ai.gemini import Gemini


class GeminiTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_i18n = MagicMock()
        self.mock_i18n.get.side_effect = lambda key, **kwargs: key

        self.logger = logging.getLogger('ai.gemini')
        self.logger.disabled = True

        self.gemini = Gemini()

    def tearDown(self):
        self.mock_i18n = None
        self.logger.disabled = False
        self.gemini = None

    async def test_gemini(self):

        cases = [
            ("", "error-no-token"),
            ("   ", "error-no-token"),
            ("bad-token", "error-invalid-token"),
            ("кирилиця в токені", "error-invalid-token"),
        ]

        for token, error_msg in cases:

            with self.subTest(token=token, error_msg=error_msg):

                self.assertEqual(
                    await self.gemini.query(
                        i18n=self.mock_i18n,
                        token=token,
                        global_prompt="test",
                        local_prompt="test",
                    ),
                    error_msg,
                )
