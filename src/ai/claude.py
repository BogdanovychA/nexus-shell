from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext

import logging

import anthropic

from ai.abstract import AIModel
from models import AIModels
from utils import constants

logger = logging.getLogger(__name__)


class Claude(AIModel):

    NAME = AIModels.CLAUDE
    TOKEN_URL = constants.CLAUDE_URL

    async def query(
        self, i18n: I18nContext, token: str, global_prompt: str, local_prompt: str
    ) -> str:

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

        except anthropic.APIStatusError as e:
            error_msg = str(e)

            if "invalid_request_error" in error_msg.lower():
                text = i18n.get(
                    "error-balance-is-low", name=self.NAME, token_url=self.TOKEN_URL
                )
            else:
                text = i18n.get("error-client-api", name=self.NAME)

            logger.warning("ClientError in %s: %s", self.NAME, error_msg)

        except Exception as e:
            text = f'{i18n.get("info-forward-text")}\n\n{i18n.get("error-unexpected", name=self.NAME, error=str(e))}'
            logger.exception("Unexpected error in %s", self.NAME)

        return text
