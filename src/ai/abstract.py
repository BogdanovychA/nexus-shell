# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext

import logging
from abc import ABC, abstractmethod

import anthropic
import openai
from google import genai
from google.genai import errors, types

from models import AIModels
from utils import constants

logger = logging.getLogger(__name__)


class AIModel(ABC):

    NAME = "AI"
    TOKEN_URL = "https://google.com :)"

    @staticmethod
    def clean_token(token: str) -> str | None:
        token = token.strip()
        return token if token else None

    @abstractmethod
    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:
        pass


class Claude(AIModel):

    NAME = AIModels.CLAUDE
    TOKEN_URL = constants.CLAUDE_URL

    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:

        text = ""

        if not (token := self.clean_token(token)):
            return i18n.get("error-no-token", name=self.NAME)

        try:
            client = anthropic.AsyncAnthropic(api_key=token)

            response = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                # claude-sonnet-4-5-20250929, claude-opus-4-20250812,
                # claude-haiku-4-5-20251001, claude-sonnet-4-20250514
                max_tokens=3000,
                system=global_prompt,
                messages=[{"role": "user", "content": local_prompt}],
            )

            return response.content[0].text.strip()

        except UnicodeEncodeError as e:
            text = i18n.get(
                "error-forbidden-chars", name=self.NAME, token_url=self.TOKEN_URL
            )
            logger.warning("UnicodeEncodeError in %s: %s", self.NAME, e)

        except anthropic.AuthenticationError as e:
            text = i18n.get(
                "error-invalid-token", name=self.NAME, token_url=self.TOKEN_URL
            )
            logger.warning("AuthenticationError in %s: %s", self.NAME, e)

        except Exception as e:
            text = f'{i18n.get("info-forward-text")}\n\n{i18n.get("error-unexpected", name=self.NAME, error=str(e))}'
            logger.exception("Unexpected error in %s", self.NAME)

        return text


class ChatGPT(AIModel):

    NAME = AIModels.GPT
    TOKEN_URL = constants.CHATGPT_URL

    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:

        text = ""

        if not (token := self.clean_token(token)):
            return i18n.get("error-no-token", name=self.NAME)

        try:
            client = openai.AsyncOpenAI(api_key=token)

            model = "gpt-4-turbo"  # gpt-4-turbo, gpt-4o, gpt-4-turbo, gpt-3.5-turbo

            message_list = [
                {"role": "system", "content": global_prompt},
                {"role": "user", "content": local_prompt},
            ]

            response = await client.chat.completions.create(
                model=model,
                messages=message_list,
                max_tokens=2000,
                temperature=0.9,
                n=1,
            )

            text = response.choices[0].message.content.strip()

        except openai.AuthenticationError as e:
            text = i18n.get(
                "error-invalid-token", name=self.NAME, token_url=self.TOKEN_URL
            )
            logger.warning("AuthenticationError in %s: %s", self.NAME, e)

        except Exception as e:
            text = f'{i18n.get("info-forward-text")}\n\n{i18n.get("error-unexpected", name=self.NAME, error=str(e))}'
            logger.exception("Unexpected error in %s", self.NAME)

        return text


class Gemini(AIModel):

    NAME = AIModels.GEMINI
    TOKEN_URL = constants.GEMINI_URL

    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:

        text = ""

        if not (token := self.clean_token(token)):
            return i18n.get("error-no-token", name=self.NAME)

        try:
            client = genai.Client(api_key=token)

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",  # gemini-2.5-flash, gemini-2.5-pro
                config=types.GenerateContentConfig(
                    system_instruction=global_prompt,
                    temperature=0.9,
                    # max_output_tokens=3000,
                ),
                contents=local_prompt,
            )

            text = response.text.strip()

        except errors.ClientError as e:
            error_msg = str(e)

            if "API_KEY_INVALID".lower() in error_msg.lower():
                text = i18n.get(
                    "error-invalid-token", name=self.NAME, token_url=self.TOKEN_URL
                )
            elif "RESOURCE_EXHAUSTED".lower() in error_msg.lower():
                text = i18n.get(
                    "error-limit-exhausted", name=self.NAME, token_url=self.TOKEN_URL
                )
            elif "API_KEY_INVALID".lower() in error_msg.lower():
                text = i18n.get(
                    "error-access-denied", name=self.NAME, token_url=self.TOKEN_URL
                )
            else:
                text = i18n.get("error-client-api", name=self.NAME)

            logger.warning("ClientError in %s: %s", self.NAME, error_msg)

        except ValueError as e:
            text = i18n.get(
                "error-token-format",
                name=self.NAME,
                token_url=self.TOKEN_URL,
                error=str(e),
            )
            logger.warning("ValueError (invalid token format) in %s: %s", self.NAME, e)

        except Exception as e:
            text = f'{i18n.get("info-forward-text")}\n\n{i18n.get("error-unexpected", name=self.NAME, error=str(e))}'
            logger.exception("Unexpected error in %s", self.NAME)

        return text
