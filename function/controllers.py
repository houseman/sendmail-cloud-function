import base64
from datetime import datetime
import json
import logging

import requests

from typing import Dict, Tuple

from google.cloud.functions.context import Context
from google.cloud import datastore

from exceptions import (
    PayloadError,
    BaseError,
    DuplicateMessageError,
    ApiResponseError,
)
from models import ApiResponse, ControllerResponse, MailMessage
from config import Config


class Controller:
    _datastore_client = datastore.Client()
    _config = Config()

    def send(self, event: Dict, context: Context) -> ControllerResponse:
        try:

            message = self._get_message_from_payload()
            result = self._send_message(message, context)

            logging.info(
                f"{self._config.MAILGUN_HOST} replied: [{result.status_code}] {result.text}"
            )

            return ControllerResponse(
                message=result.text, response_code=result.status_code
            )
        except DuplicateMessageError as error:
            logging.error(f"{error}")

            return ControllerResponse(message=f"{error}", response_code=429)
        except ApiResponseError as error:
            logging.error(f"{error}")

            return ControllerResponse(
                message=error.text, response_code=error.result_code
            )

    def _send_message(self, message: MailMessage, context: Context) -> Dict:
        with self._datastore_client.transaction():
            key = self._datastore_client.key("EmailTransactionLog", context.event_id)

            transaction_log = self._datastore_client.get(key)

            if not transaction_log:
                # Create the Entity if the key doesnot exist
                transaction_log = datastore.Entity(key)

            if transaction_log.get("completed_at"):
                raise DuplicateMessageError(
                    f"Message ID {context.event_id} previously completed"
                )

            result = self._send_to_api(message)

            if result.status_code == 200:
                transaction_log.update({"completed_at": datetime.now()})
                self._datastore_client.put(transaction_log)

            return result.text, result.status_code

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
        except AttributeError as error:
            error_message = f"Badly-formed message: Attribute {error} not found"
            logging.error(error_message)

            raise PayloadError(error_message)
        except Exception as error:
            """ If a message could not be decoded from the payload, return (400)"""
            error_message = f"Message payload could not be decoded: {error}"
            logging.error(error_message)

            raise PayloadError(message=error_message, status_code=400)

    def _send_to_api(self, message) -> ApiResponse:
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
        return ApiResponse(response_code=response.status_code, message=response.text)
