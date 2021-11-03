import logging
from typing import Dict

from exceptions import ApiError, ControllerError, PayloadError
from integrations import Mailgun
from responses import ControllerResponse
from utils import create_message_from_payload


class SendController:
    """Controller class that contains logic for sending an Email contained within
    the encoded Pub/Sub message.
    """

    def __init__(self) -> None:
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
            message = create_message_from_payload(event)
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
