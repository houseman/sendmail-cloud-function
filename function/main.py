from typing import Dict, Tuple

from google.cloud.functions.context import Context

from function.cloudfunc.config import Config
from function.cloudfunc.controllers import Controller


def cloud_send_mail(event: Dict, context: Context) -> Tuple[str, int]:
    """Entrypoint: A background Google Cloud Function to be triggered by a Pub/Sub
    message.

    ### Args:
    - `event`: Dict contains event data;
      - `event["data"]`: contains the PubsubMessage message.
      - `event["attributes"]`: contain custom attributes if there are any.
    - `context`: Context Event metadata (if any).
      - `context.event_id`: int The Pub/Sub message ID.
      - `context.timestamp`: datetime The message publish time.

    ### Returns:
    A Tuple of (message: str, response_code: int)
    """
    logger = Config.create_logger()
    controller = Controller(logger)
    logger.info(f"{__name__} triggered with event_id {context.event_id}")
    response = controller.send(event, context)
    logger.info(f"Event {context.event_id} result: {response}")
    return (response.message, response.response_code)
