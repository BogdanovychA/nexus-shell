# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod

import anthropic
import openai
from google import genai
from google.genai import errors, types

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
    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:
        pass


class Claude(AIModel):

    NAME = "Claude"
    TOKEN_URL = constants.CLAUDE_URL

    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:

        text = ""

        if not (token := self.clean_token(token)):
            return "API-ключ (токен) {NAME} відсутній у налаштуваннях.\nНалаштуй: /setup".format(
                NAME=self.NAME
            )

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
            text = "API-ключ (токен) {NAME} містить заборонені символи.\nНалаштуй інший: /setup\n\n".format(
                NAME=self.NAME
            ) + "Отримати можна тут: {TOKEN_URL}".format(
                TOKEN_URL=self.TOKEN_URL
            )
            logger.warning("UnicodeEncodeError in %s: %s", self.NAME, e)

        except anthropic.AuthenticationError as e:
            text = "API-ключ (токен) {NAME} недійсний або термін його дії закінчився.\nНалаштуй інший: /setup\n\n".format(
                NAME=self.NAME
            ) + "Отримати можна тут: {TOKEN_URL}".format(
                TOKEN_URL=self.TOKEN_URL
            )
            logger.warning("AuthenticationError in %s: %s", self.NAME, e)

        except Exception as e:
            text = "{FORWARD_TEXT}\nНеочікувана помилка при зверненні до {NAME}:\n\n{e}".format(
                FORWARD_TEXT=constants.FORWARD_TEXT, NAME=self.NAME, e=str(e)
            )
            logger.exception("Unexpected error in %s", self.NAME)

        return text


class ChatGPT(AIModel):

    NAME = "ChatGPT"
    TOKEN_URL = constants.CHATGPT_URL

    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:

        text = ""

        if not (token := self.clean_token(token)):
            return "API-ключ (токен) {NAME} відсутній у налаштуваннях.\nНалаштуй: /setup".format(
                NAME=self.NAME
            )

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
            text = "API-ключ (токен) {NAME} недійсний або термін його дії закінчився.\nНалаштуй інший: /setup\n\n".format(
                NAME=self.NAME
            ) + "Отримати можна тут: {TOKEN_URL}".format(
                TOKEN_URL=self.TOKEN_URL
            )
            logger.warning("AuthenticationError in %s: %s", self.NAME, e)

        except Exception as e:
            text = "{FORWARD_TEXT}\nНеочікувана помилка при зверненні до {NAME}:\n\n{e}".format(
                FORWARD_TEXT=constants.FORWARD_TEXT, NAME=self.NAME, e=str(e)
            )
            logger.exception("Unexpected error in %s", self.NAME)

        return text


class Gemini(AIModel):

    NAME = "Gemini"
    TOKEN_URL = constants.GEMINI_URL

    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:

        text = ""

        if not (token := self.clean_token(token)):
            return "API-ключ (токен) {NAME} відсутній у налаштуваннях.\nНалаштуй: /setup".format(
                NAME=self.NAME
            )

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

            if "API_KEY_INVALID".lower() in error_msg.lower() or "400" in error_msg:
                text = "API-ключ (токен) {NAME} недійсний або термін його дії закінчився.\nНалаштуй інший: /setup\n\n".format(
                    NAME=self.NAME
                ) + "Отримати можна тут: {TOKEN_URL}".format(
                    TOKEN_URL=self.TOKEN_URL
                )
            elif (
                "RESOURCE_EXHAUSTED".lower() in error_msg.lower() or "429" in error_msg
            ):
                text = (
                    "Ти вичерпав ліміт за цим API-ключем (токеном).\nСпробуй пізніше або налаштуй інший: /setup\n\n"
                    + "Отримати можна тут: {TOKEN_URL}".format(TOKEN_URL=self.TOKEN_URL)
                )
            elif "API_KEY_INVALID".lower() in error_msg.lower() or "403" in error_msg:
                text = (
                    "Доступ за цим API-ключем (токеном) заборонений.\nНалаштуй інший: /setup\n\n"
                    + "Отримати можна тут: {TOKEN_URL}".format(TOKEN_URL=self.TOKEN_URL)
                )
            else:
                text = "{FORWARD_TEXT}\nПомилка клієнта {NAME} (API)".format(
                    FORWARD_TEXT=constants.FORWARD_TEXT, NAME=self.NAME
                )

            logger.warning("ClientError in %s: %s", self.NAME, error_msg)

        except ValueError as e:
            text = "Некоректний формат токена.\n\n{e}".format(e=str(e))
            logger.warning("ValueError (invalid token format) in %s: %s", self.NAME, e)

        except Exception as e:
            text = "{FORWARD_TEXT}\nНеочікувана помилка при зверненні до {NAME}:\n\n{e}".format(
                FORWARD_TEXT=constants.FORWARD_TEXT, NAME=self.NAME, e=str(e)
            )
            logger.exception("Unexpected error in %s", self.NAME)

        return text
