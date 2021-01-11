import base64
import json
import requests
import logging

from typing import Dict

from google.cloud.functions.context import Context

from config import Config

Config().create_logger()
CONFIG = Config()


def salepen_send_mail(event: Dict, context: Context) -> None:
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

    if "data" in event:
        try:
            payload = base64.b64decode(event["data"]).decode("utf-8")
            message = json.loads(payload)
        except Exception as error:
            """ If a message could not be decoded from the payload, return (400)"""
            error_message = f"A message payload could not be decoded: {error}"
            logging.error(error_message)

            return error_message, 400

        result = requests.post(
            f"https://{CONFIG.MAILGUN_HOST}/v3/mg.stockfair.net/messages",
            auth=("api", CONFIG.MAILGUN_API_SENDING_KEY),
            data={
                "from": "SalePen <admin@stockfair.net>",
                "to": [message["rcpt"]],
                "subject": message["subject"] + f" {context.event_id}",
                "html": message["html_content"],
                "text": message["text_content"],
            },
        )

        logging.info(
            f"{CONFIG.MAILGUN_HOST} replied: [{result.status_code}] {result.text}"
        )

        return result.text, result.status_code

    # If no data is set, just log and return. Do not raise an error as this will
    # cause a retry on a bad message that is not valid
    logging.error("No data set in event")
    return "No data set in event", 400
