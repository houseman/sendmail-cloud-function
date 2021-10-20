import base64
import json
from logging import Logger
from typing import Dict, Optional

import requests
from google.cloud.functions.context import Context

from function.cloudfunc.config import Config
from function.cloudfunc.exceptions import ApiResponseError, PayloadError
from function.cloudfunc.models import ApiResponse, ControllerResponse, MailMessage


class Controller:
    """Controller class that contains logic for sending an Email contained within
    the encoded Pub/Sub message.
    """

    _config = Config()

    def __init__(self, logger: Optional[Logger] = None) -> None:
        if not logger:
            logger = Config.create_logger()
        self.logger = logger

    def send(self, event: Dict, context: Context) -> ControllerResponse:
        """Send an email contained within the encoded Pub/Sub message}.

        ### Args:
        - event: Dict contains event data;
        - context: Context Event metadata (if any).

        ### Returns:
        - ControllerResponse
        """
        try:
            message = self._get_message_from_payload(event)
            result = self._send_message(message, context)
            self.logger.info(f"{result}")

            return ControllerResponse(
                message=result.message, response_code=result.response_code
            )
        except Exception as error:
            self.logger.error(f"{error}")
            raise error

    def _send_message(self, message: MailMessage, context: Context) -> ApiResponse:
        """Send a `MailMessage` object data to the *Mailgun* endpoint."""

        try:
            host = self._config.get_val("MAILGUN_HOST")
            domain = self._config.get_val("MAILGUN_DOMAIN")
            api_key = self._config.get_val("MAILGUN_API_SENDING_KEY")

            response = requests.post(
                f"https://{host}/v3/{domain}/messages",
                auth=("api", api_key),
                data={
                    "from": message.sender,
                    "to": [message.recipient],
                    "subject": message.subject,
                    "html": message.html_content,
                    "text": message.text_content,
                },
            )
            self.logger.info(f"Server {host} replied: {response}")

            # If no error was raised, map response to a `ApiResponse` object and return
            return ApiResponse(
                response_code=response.status_code, message=response.text
            )
        except Exception as error:
            self.logger.error(f"{error}")
            raise ApiResponseError(status_code=500, message=f"{error}")

    def _get_message_from_payload(self, event: Dict) -> MailMessage:
        """Return a `MailMessage` object, populated with data from the Pub/Sub message
        payload.
        """

        try:
            message = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
            return MailMessage(
                recipient=message["rcpt"],
                sender=message["sender"],
                subject=message["subject"],
                html_content=message["html_content"],
                text_content=message["text_content"],
            )
        except Exception as error:
            # If a message could not be decoded from the payload, return (400)

            error_message = f"Message payload could not be decoded: {error}"
            self.logger.error(error_message)
            raise PayloadError(message=error_message, status_code=400)
