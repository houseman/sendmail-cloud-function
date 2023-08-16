from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import google.cloud.logging
from send_mail.controllers import SendController

if TYPE_CHECKING:
    from google.cloud.functions.context import Context

# Below 2 lines retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the Python logging module.
# By default this captures all logs at INFO level and higher
client = google.cloud.logging.Client()
client.setup_logging()

controller = SendController()


def cloud_send_mail(event: dict, context: Context) -> tuple[str, int]:
    """A Google Cloud Function triggered by a Pub/Sub message.
    Returns a tuple of (message: str, response_code: int)

    **Note** Use the `--entry-point` flag to specify this function name when deploying.

    **Note** Cloud Functions looks for deployable functions in `main.py` by default.
    Use the `--source` flag when deploying your function via gcloud to specify
    a different directory containing a `main.py` file.

    By default, if a function invocation terminates with an error, the function will
    *not* be invoked again, and the event will be dropped. When you enable retries on
    an event-driven function, Cloud Functions will retry a failed function invocation
    until it completes successfully, or the retry window (by default, 7 days) expires.
    """

    logging.info(f"{__name__} triggered by event {context.event_id}")

    response = controller.send(event)

    logging.info(f"Event {context.event_id} returned {response}")

    return (response.message, response.response_code)
