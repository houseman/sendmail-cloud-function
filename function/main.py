import logging
from typing import Dict, Tuple

from cloudfunc.config import Config
from cloudfunc.controllers import Controller
from google.cloud.functions.context import Context

Config().create_logger()

controller = Controller()


def salepen_send_mail(event: Dict, context: Context) -> Tuple[str, int]:
    """A background Google Cloud Function to be triggered by a Pub/Sub message.

    Args:
         event: Dict contains event data;
         - event["data"]: contains the PubsubMessage message.
         - event["attributes"]: contain custom attributes if there are any.
         context: Context Event metadata (if any).
         - context.event_id: int The Pub/Sub message ID.
         - context.timestamp: datetime The message publish time.

     Returns:
          A Tuple of (message: str, response_code: int)
    """

    logging.info(f"{__name__} triggered with event_id {context.event_id}")

    controller = Controller()
    response = controller.send(event, context)

    return (response.message, response.response_code)
