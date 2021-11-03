import base64
import json
import logging
from typing import Dict

from exceptions import PayloadError
from schemas import MailMessage


def create_message_from_payload(event: Dict) -> MailMessage:
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
