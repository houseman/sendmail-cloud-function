import logging
from typing import Optional

import google.auth
import google.cloud.logging
from google.api_core.exceptions import PermissionDenied as PermissionDeniedError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import secretmanager_v1 as secretmanager


class Config:
    MAILGUN_API_SENDING_KEY: Optional[str] = None
    MAILGUN_HOST: str = "api.mailgun.net"

    secret_manager = secretmanager.SecretManagerServiceClient()

    def __init__(self) -> None:
        if not self.MAILGUN_API_SENDING_KEY:
            self.MAILGUN_API_SENDING_KEY = self._get_mailgun_api_sending_key()

    def _get_mailgun_api_sending_key(self) -> Optional[str]:
        try:
            _, project = google.auth.default()

            secret_name = "mailgun-api-sending-key"
            secret_path = f"projects/{project}/secrets/{secret_name}/versions/latest"
            mailgun_api_sending_key = self.secret_manager.access_secret_version(
                name=secret_path
            ).payload.data.decode("UTF-8")

            if not mailgun_api_sending_key:
                logging.error("MAILGUN_API_SENDING_KEY not set. Cannot continue.")

                # If a key could not be attained, raise an excpetion
                # as this message should be retried
                raise Exception("MAILGUN_API_SENDING_KEY not set. Cannot continue.")

            return mailgun_api_sending_key

        except PermissionDeniedError as exception:
            logging.error(exception)

            # Raise exception, so that PubSub will retry
            raise Exception(exception)

        except DefaultCredentialsError as exception:
            logging.error(exception)

            # Raise exception, so that PubSub will retry
            raise Exception(exception)

    @staticmethod
    def create_logger():
        try:
            logging_client = google.cloud.logging.Client()
            logging_client.get_default_handler()
            logging_client.setup_logging()

            return logging_client

        except DefaultCredentialsError as exception:
            logging.error(exception)
            raise Exception("Could not create a logging client")
