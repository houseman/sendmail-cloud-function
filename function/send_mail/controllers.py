import base64
import json
import logging

from .exceptions import ApiException, ControllerException, PayloadException
from .integrations import MailgunIntegration
from .responses import ControllerResponse
from .dtos import MailMessageDTO


class SendController:
    """Controller class that contains logic for sending an email message contained
    within an encoded Pub/Sub message.
    """

    def __init__(self) -> None:
        self._integration = MailgunIntegration()

    def send(self, event: dict) -> ControllerResponse:
        """Send an email contained within the encoded Pub/Sub message}"""

        try:
            message = self.get_message_from_payload(event)
            result = self._integration.send(message)
            logging.info(f"{result}")

            return ControllerResponse(
                message=result.message, response_code=result.response_code
            )
        except PayloadException:
            # Swallow this exception, as we do not want to retry badly-formatted
            # messages
            return ControllerResponse(message="Bad Request", response_code=400)
        except ApiException as error:
            logging.error(f"{error}")
            raise ControllerException(
                message=error.message, status_code=error.status_code
            )

    @staticmethod
    def get_message_from_payload(event: dict) -> MailMessageDTO:
        """Return a `MailMessageDTO` object, populated with data from the Pub/Sub
        message payload.
        """

        try:
            message = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
            return MailMessageDTO(
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
            raise PayloadException(message=error_message, status_code=400)
