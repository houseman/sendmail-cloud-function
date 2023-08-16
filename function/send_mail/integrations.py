from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import requests
from .config import get_env_int, get_env_str
from .exceptions import ApiException
from .responses import ApiResponse

if TYPE_CHECKING:
    from .dtos import MailMessageDTO


class MailgunIntegration:
    """Mailgun <https://www.mailgun.com/> service integration"""

    def __init__(self) -> None:
        self._session = requests.Session()
        self.host = get_env_str("MAILGUN_HOST")
        self.domain = get_env_str("MAILGUN_DOMAIN")
        self.api_key = get_env_str("MAILGUN_API_SENDING_KEY")
        self.timeout = get_env_int("MAILGUN_TIMEOUT", 30)

    def send(self, message: MailMessageDTO) -> ApiResponse:
        """Send a `MailMessageDTO` object data to the Mailgun API endpoint"""

        try:
            response = self._session.post(
                url=f"https://{self.host}/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data={
                    "from": message.sender,
                    "to": [message.recipient],
                    "subject": message.subject,
                    "html": message.html_content,
                    "text": message.text_content,
                },
                timeout=self.timeout,
            )
            logging.info(f"Server {self.host} replied: {response}")
            # Raise an HTTPError if the HTTP request returned an unsuccessful status
            # code
            response.raise_for_status()
            # If no error was raised, map response to a `ApiResponse` object and return
            return ApiResponse(
                response_code=response.status_code, message=response.text
            )
        except requests.exceptions.HTTPError as error:
            logging.error(f"{error}")
            raise ApiException(
                status_code=error.response.status_code, message=f"{error}"
            )
