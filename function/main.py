import logging
from typing import Dict, Tuple

from controllers import SendController
from google.cloud.functions.context import Context

logger = logging.getLogger(__name__)
controller = SendController()


def cloud_send_mail(event: Dict, context: Context) -> Tuple[str, int]:
    """A background _Google Cloud Function_ to be triggered by a Pub/Sub
    message.
    **Entrypoint:** Use the `--entry-point` flag to specify this function name when
    deploying to GCP.
    **Note:** _Cloud Functions_ looks for deployable functions in `main.py` by
    default. Use the `--source` flag when deploying your function via gcloud to specify
    a different directory containing a `main.py` file.

    ### Args:
    - `event`: Dict contains event data;
      - `event["data"]`: contains the PubsubMessage message.
      - `event["attributes"]`: contain custom attributes if there are any.
    - `context`: Context Event metadata (if any).
      - `context.event_id`: int The Pub/Sub message ID.
      - `context.timestamp`: datetime The message publish time.

    ### Returns:
    A Tuple of (message: str, response_code: int)

    ### Raises:
    - `Retry`: An exception that indicates retry should be attempted.

    By default, if a function invocation terminates with an error, the function will
    *not* be invoked again, and the event will be dropped. When you enable retries on
    an event-driven function, Cloud Functions will retry a failed function invocation
    until it completes successfully, or the retry window (by default, 7 days) expires.
    """

    logger.info(f"{__name__} triggered with event_id {context.event_id}")
    response = controller.send(event)
    logger.info(f"Event {context.event_id} result: {response}")

    return (response.message, response.response_code)
