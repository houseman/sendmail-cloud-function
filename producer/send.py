import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

import dotenv
import html2text
from google.api_core.exceptions import NotFound as TopicNotFoundException
from google.cloud import pubsub_v1

logger = logging.Logger(__name__)

dotenv.load_dotenv(".env")
GCLOUD_PROJECT_ID = os.environ.get("GCLOUD_PROJECT_ID")
PUBSUB_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID")


@dataclass
class MailMessage:
    recipient: str
    subject: str
    html_content: str
    text_content: Optional[str] = None

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def send_email_task(
    recipient: str, subject: str, html_content: str, text_content: Optional[str] = None
):
    """sends an email"""

    if not text_content:
        h = html2text.HTML2Text()
        h.ignore_links = False
        text_content = h.handle(html_content)

    message = MailMessage(
        recipient=recipient,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )
    return send_message(message)


def send_message(message: MailMessage):
    message_json = message.to_json()

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, PUBSUB_TOPIC_ID)
    print(f"topic_path: {topic_path}")
    try:
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        result = future.result()
        print(f"{result}")

        return result
    except TopicNotFoundException as pubsub_error:
        logger.warn(f"Error sending pubsub: {pubsub_error}")

        return None


if __name__ == "__main__":
    send_email_task(
        recipient="scott.houseman@gmail.com",
        subject="Test from Python",
        html_content="<h1>Hello</h1>",
    )
