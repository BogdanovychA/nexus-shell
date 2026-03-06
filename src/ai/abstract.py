# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

import anthropic
import openai
from google import genai
from google.genai import errors, types

CLAUDE_URL = "https://platform.claude.com/settings/keys"
CHATGPT_URL = "https://platform.openai.com/account/api-keys"
GEMINI_URL = "https://aistudio.google.com/app/api-keys"


class AIModel(ABC):

    NAME = "AI"
    TOKEN_URL = "https://google.com :)"

    @abstractmethod
    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:
        pass


class Claude(AIModel):

    NAME = "Claude"
    TOKEN_URL = CLAUDE_URL

    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:

        # token = token.strip()
        # if not token:
        #     return f"API-ключ (токен) {self.NAME} відсутній у налаштуваннях.\nНалаштуй: /setup"

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
            text = (
                f"API-ключ (токен) {self.NAME} містить заборонені символи.\nНалаштуй інший: /setup\n\n"
                + f"Отримати можна тут: {self.TOKEN_URL}"
            )
            print(e)

        except anthropic.AuthenticationError as e:
            text = (
                f"API-ключ (токен) {self.NAME} недійсний або термін його дії закінчився.\nНалаштуй інший: /setup\n\n"
                + f"Отримати можна тут: {self.TOKEN_URL}"
            )
            print(e)

        except Exception as e:
            text = f"Неочікувана помилка при зверненні до {self.NAME}:\n\n{str(e)}"
            print(e)

        return text


class ChatGPT:

    NAME = "ChatGPT"
    TOKEN_URL = CHATGPT_URL

    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:

        token = token.strip()

        if not token:
            return f"API-ключ (токен) {self.NAME} відсутній у налаштуваннях.\nНалаштуй: /setup"

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
            text = (
                f"API-ключ (токен) {self.NAME} недійсний або термін його дії закінчився.\nНалаштуй інший: /setup\n\n"
                + f"Отримати можна тут: {self.TOKEN_URL}"
            )
            print(e)
        except Exception as e:
            text = f"Неочікувана помилка при зверненні до {self.NAME}:\n\n{str(e)}"
            print(e)

        return text


class Gemini(AIModel):

    NAME = "Gemini"
    TOKEN_URL = GEMINI_URL

    async def query(self, token: str, global_prompt: str, local_prompt: str) -> str:

        token = token.strip()

        if not token:
            return f"API-ключ (токен) {self.NAME} відсутній у налаштуваннях.\nНалаштуй: /setup"

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

            if "API_KEY_INVALID" in error_msg or "400" in error_msg:
                text = (
                    f"API-ключ (токен) {self.NAME} недійсний або термін його дії закінчився.\nНалаштуй інший: /setup\n\n"
                    + f"Отримати можна тут: {self.TOKEN_URL}"
                )
            elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                text = (
                    f"Ти вичерпав ліміт за цим API-ключем (токеном).\nСпробуй пізніше або налаштуй інший: /setup\n\n"
                    + f"Отримати можна тут: {self.TOKEN_URL}"
                )
            elif "API_KEY_INVALID" in error_msg or "403" in error_msg:
                text = (
                    f"Доступ за цим API-ключем (токеном) заборонений.\nНалаштуй інший: /setup\n\n"
                    + f"Отримати можна тут: {self.TOKEN_URL}"
                )
            else:
                text = f"Помилка клієнта {self.NAME} (API)"

            print(error_msg)

        except ValueError as e:
            text = f"Некоректний формат токена.\n\n{str(e)}"
            print(e)

        except Exception as e:
            text = f"Неочікувана помилка при зверненні до {self.NAME}:\n\n{str(e)}"
            print(e)

        return text
