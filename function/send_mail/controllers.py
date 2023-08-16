import base64
import json
import logging

from .config import Config
from .exceptions import ApiError, ControllerError, PayloadError
from .integrations import Mailgun
from .responses import ControllerResponse
from .schemas import MailMessage


class SendController:
    """Controller class that contains logic for sending an Email contained within
    the encoded Pub/Sub message.
    """

    _config = Config()

    def __init__(self) -> None:
        self._integration = Mailgun()

    def send(self, event: dict) -> ControllerResponse:
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
            logging.info(f"{result}")

            return ControllerResponse(
                message=result.message, response_code=result.response_code
            )
        except PayloadError:
            # Swallow this exception, as we do not want to retry badly-formatted
            # messages
            return ControllerResponse(message="Bad Request", response_code=400)
        except ApiError as error:
            logging.error(f"{error}")
            raise ControllerError(message=error.message, status_code=error.status_code)

    def _get_message_from_payload(self, event: dict) -> MailMessage:
        """Return a `MailMessage` object, populated with data from the Pub/Sub message
        payload.
        """

        try:
            message = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
            return MailMessage(
                recipient=message["recipient"],
                sender=message["sender"],
                subject=message["subject"],
                html_content=message["html_content"],
                text_content=message["text_content"],
            )
        except Exception as error:
            # If a message could not be decoded from the payload, return (400)

            error_message = f"Message payload could not be decoded: {error}"
            logging.error(error_message)
            raise PayloadError(message=error_message, status_code=400)
