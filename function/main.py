import logging
from typing import Dict, Tuple

from config import Config
from controllers import Controller
from google.cloud.functions.context import Context

Config().create_logger()

controller = Controller()


def salepen_send_mail(event: Dict, context: Context) -> Tuple[str, int]:
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict): Dict contains event data;
         event["data"]: contains the PubsubMessage message.
         event["attributes"]: contain custom attributes if there are any.
         context (google.cloud.functions.Context): event metadata.
         context.event_id: the Pub/Sub message ID.
         context.timestamp: contains the publish time.
    """
    logging.info(f"{__name__} triggered with event_id {context.event_id}")
    controller = Controller()
    response = controller.send(event, context)

    return (response.message, response.response_code)
