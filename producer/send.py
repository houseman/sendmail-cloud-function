import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

import click
import dotenv
import html2text
from google.api_core.exceptions import NotFound as TopicNotFoundException
from google.cloud import pubsub_v1

logger = logging.Logger(__name__)


@dataclass
class MailMessage:
    recipient: str
    sender: str
    subject: str
    html_content: str
    text_content: Optional[str] = None

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def get_env_file_path() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, ".env")


@click.command()
@click.option(
    "--to", "-t", "recipient", required=True, type=str, help="Recipient email address"
)
@click.option("--subject", "-s", required=True, type=str, help="Email subject")
@click.option(
    "--message",
    "-m",
    "html_content",
    required=True,
    type=str,
    help="Email message (HTML)",
)
def send_email_task(
    recipient: str, subject: str, html_content: str, text_content: Optional[str] = None
) -> Optional[str]:
    """sends an email"""

    if not text_content:
        h = html2text.HTML2Text()
        h.ignore_links = False
        text_content = h.handle(html_content)

    message = MailMessage(
        recipient=recipient,
        sender=FROM_ADDR,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )
    return send_message(message)


def send_message(message: MailMessage) -> Optional[str]:
    message_json = message.to_json()

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, PUBSUB_TOPIC_ID)
    try:
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        result = future.result()
        print(f"Publisheed message ID {result} to topic {topic_path}")

        return result
    except TopicNotFoundException as pubsub_error:
        logger.error(f"Error sending pubsub: {pubsub_error}")

        return None


if __name__ == "__main__":
    dotenv.load_dotenv(get_env_file_path())
    GCLOUD_PROJECT_ID = os.environ.get("GCLOUD_PROJECT_ID")
    PUBSUB_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID")
    FROM_ADDR = str(os.environ.get("FROM_ADDR"))

    send_email_task()
