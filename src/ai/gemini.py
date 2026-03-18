from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext

import logging

from google import genai
from google.genai import errors, types

from ai.abstract import AIModel
from models import AIModels
from utils import constants

logger = logging.getLogger(__name__)


class Gemini(AIModel):

    NAME = AIModels.GEMINI
    TOKEN_URL = constants.GEMINI_URL

    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:

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
            elif "503" in error_msg and "UNAVAILABLE".lower() in error_msg.lower():
                text = i18n.get(
                    "error-model-overloaded",
                    name=self.NAME,
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
