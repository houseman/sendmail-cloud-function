import base64
import json
from logging import Logger
from typing import Dict, Optional

from function.config import Config
from function.exceptions import ApiError, ControllerError, PayloadError
from function.integrations import Mailgun
from function.responses import ControllerResponse
from function.schemas import MailMessage


class SendController:
    """Controller class that contains logic for sending an Email contained within
    the encoded Pub/Sub message.
    """

    _config = Config()

    def __init__(self, logger: Optional[Logger] = None) -> None:
        if not logger:
            logger = Config.create_logger()
        self.logger = logger
        self._integration = Mailgun()

    def send(self, event: Dict) -> ControllerResponse:
        """Send an email contained within the encoded Pub/Sub message}.

        ### Args:
        - event: Dict contains event data;

        ### Returns:
        - ControllerResponse

        ### Raises:
        - ControllerError
        """
        try:
            message = self._get_message_from_payload(event)
            result = self._integration.send(message)
            self.logger.info(f"{result}")

            return ControllerResponse(
                message=result.message, response_code=result.response_code
            )
        except PayloadError:
            # Swallow this exception, as we do not want to retry badly-formatted
            # messages
            return ControllerResponse(message="Bad Request", response_code=400)
        except ApiError as error:
            self.logger.error(f"{error}")
            raise ControllerError(message=error.message, status_code=error.status_code)

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
