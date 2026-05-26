from __future__ import annotations

from typing import TYPE_CHECKING

import openai

from ai.abstract import AIModel
from models import AIModels
from utils import constants

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext

import logging

logger = logging.getLogger(__name__)


class Lapathoniia(AIModel):
    NAME = AIModels.LAPA
    TOKEN_URL = constants.LAPATHONIIA_URL

    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:

        if not (token := self.clean_token(token)):
            return i18n.get("error-no-token", name=self.NAME)

        try:
            client = openai.AsyncOpenAI(
                api_key=token, base_url="https://api.lapathoniia.top"
            )

            model = "MamayLM-Gemma-3-12B-IT-v1.0"  # LapaLLM-Gemma-3-12B-v0.1.2-instruct

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

            message = response.choices[0].message
            text = message.content.strip() if message.content else ""

        except UnicodeEncodeError as e:
            text = i18n.get(
                "error-forbidden-chars", name=self.NAME, token_url=self.TOKEN_URL
            )
            logger.warning("UnicodeEncodeError in %s: %s", self.NAME, e)

        except openai.AuthenticationError as e:
            text = i18n.get(
                "error-invalid-token", name=self.NAME, token_url=self.TOKEN_URL
            )
            logger.warning("AuthenticationError in %s: %s", self.NAME, e)

        except openai.RateLimitError as e:
            error_msg = str(e)

            text = i18n.get(
                "error-limit-exhausted", name=self.NAME, token_url=self.TOKEN_URL
            )

            logger.warning("ClientError in %s: %s", self.NAME, error_msg)

        except Exception as e:
            text = f'{i18n.get("info-forward-text")}\n\n{i18n.get("error-unexpected", name=self.NAME, error=str(e))}'
            logger.exception("Unexpected error in %s", self.NAME)

        return text
