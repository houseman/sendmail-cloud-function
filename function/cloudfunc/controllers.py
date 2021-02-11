import base64
import json
import logging
from datetime import datetime
from typing import Dict

import requests
from cloudfunc.config import Config
from cloudfunc.exceptions import ApiResponseError, PayloadError
from cloudfunc.models import (
    ApiResponse,
    ControllerResponse,
    MailMessage,
    TransactionRecord,
)
from cloudfunc.utils import TransactionUtil
from google.cloud.functions.context import Context


class Controller:
    """Controller class that contains logic for sending an Email contained within
    the encoded Pub/Sub message.
    """

    _config = Config()

    def send(self, event: Dict, context: Context) -> ControllerResponse:
        """Send an email contained in within the encoded Pub/Sub message}.

        Args:
            event: Dict contains event data;
            context: Context Event metadata (if any).

        Returns:
            ControllerResponse
        """
        try:

            message = self._get_message_from_payload(event)
            result = self._send_message(message, context)

            logging.info(f"{result}")

            return ControllerResponse(
                message=result.message, response_code=result.response_code
            )

        except Exception as error:
            logging.error(f"{error}")

            raise error

    def _send_message(self, message: MailMessage, context: Context) -> ApiResponse:
        tu = TransactionUtil().start()
        transaction: TransactionRecord = tu.create_entity(
            "EmailTransactionLog", context.event_id
        )
        logging.info(f"transaction log: {transaction}")
        transaction.try_count += 1
        if transaction.completed_at:
            # If `completed_at` is set, this message has been delivered
            return ApiResponse(
                response_code=429,
                message=f"Message ID {context.event_id} previously completed",
            )

        if transaction.try_count > 3:
            # Mark as "done", so that we do not try amd process again
            transaction.completed_at = datetime.now()

        result = self._send_to_api(message)

        if result.response_code == 200:
            transaction.completed_at = datetime.now()

        # Update the datastore
        tu.commit(transaction)

        return result

    def _get_message_from_payload(self, event: Dict) -> MailMessage:
        try:
            message = json.loads(base64.b64decode(event["data"]).decode("utf-8"))

            return MailMessage(
                recipient=message["rcpt"],
                sender=message["sender"],
                subject=message["subject"],
                html_content=message["html_content"],
                text_content=message["text_content"],
            )
        except Exception as error:
            """ If a message could not be decoded from the payload, return (400)"""
            error_message = f"Message payload could not be decoded: {error}"
            logging.error(error_message)

            raise PayloadError(message=error_message, status_code=400)

    def _send_to_api(self, message) -> ApiResponse:
        try:
            response = requests.post(
                f"https://{self._config.MAILGUN_HOST}/v3/mg.stockfair.net/messages",
                auth=("api", self._config.MAILGUN_API_SENDING_KEY),
                data={
                    "from": message.sender,
                    "to": [message.recipient],
                    "subject": message.subject,
                    "html": message.html_content,
                    "text": message.text_content,
                },
            )
            logging.info(f"Server {self._config.MAILGUN_HOST} replied: {response}")
            return ApiResponse(
                response_code=response.status_code, message=response.text
            )
        except Exception as error:
            logging.error(f"{error}")

            raise ApiResponseError(500, f"{error}")
