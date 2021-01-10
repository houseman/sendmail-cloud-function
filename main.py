import base64
import json
import requests
import logging  # NOQA

import google.cloud.logging
import google.auth

from typing import Dict

from google.cloud.functions.context import Context
from google.api_core.exceptions import PermissionDenied as PermissionDeniedException
from google.cloud import secretmanager_v1 as secretmanager

logging_client = google.cloud.logging.Client()
logging_client.get_default_handler()
logging_client.setup_logging()

MAILGUN_API_SENDING_KEY = None
MAILGUN_HOST = "api.mailgun.net"

try:
    _, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient()
    secret_name = "mailgun-api-sending-key"
    secret_path = f"projects/{project}/secrets/{secret_name}/versions/latest"
    MAILGUN_API_SENDING_KEY = client.access_secret_version(
        name=secret_path
    ).payload.data.decode("UTF-8")
except PermissionDeniedException as exception:
    logging.error(exception)


def salepen_send_mail(event: Dict, context: Context) -> None:
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    logging.info(f"{__name__} triggered with event_id {context.event_id}")

    if not MAILGUN_API_SENDING_KEY:
        logging.error("MAILGUN_API_SENDING_KEY not set. Cannot continue.")

        return "MAILGUN_API_SENDING_KEY not set. Cannot continue.", 401

    if "data" in event:
        payload = base64.b64decode(event["data"]).decode("utf-8")
        message = json.loads(payload)

        result = requests.post(
            f"https://{MAILGUN_HOST}/v3/mg.stockfair.net/messages",
            auth=("api", MAILGUN_API_SENDING_KEY),
            data={
                "from": "SalePen <admin@stockfair.net>",
                "to": [message["rcpt"]],
                "subject": message["subject"] + f" {context.event_id}",
                "html": message["html_content"],
                "text": message["text_content"],
            },
        )

        logging.info(f"{MAILGUN_HOST} replied: [{result.status_code}] {result.text}")

        return result.text, result.status_code

    logging.error("No data in event")
    return "No data in event", 500
