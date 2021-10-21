import requests

from function.config import Config
from function.exceptions import ApiError
from function.responses import ApiResponse
from function.schemas import MailMessage


class Mailgun:
    """Mailgun service integration"""

    _config = Config()

    def __init__(self) -> None:
        self._session = requests.Session()
        self.logger = self._config.create_logger()
        self.host = self._config.get_val("MAILGUN_HOST")
        self.domain = self._config.get_val("MAILGUN_DOMAIN")
        self.api_key = self._config.get_val("MAILGUN_API_SENDING_KEY")

    def send(self, message: MailMessage) -> ApiResponse:
        """Send a `MailMessage` object data to the *Mailgun* endpoint.
        ### Arguments:
        - message: `MailMessage` schema data class

        ### Returns:
        - ApiResponse

        ### Raises:
        - ApiError
        """

        try:
            response = self._session.post(
                f"https://{self.host}/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data={
                    "from": message.sender,
                    "to": [message.recipient],
                    "subject": message.subject,
                    "html": message.html_content,
                    "text": message.text_content,
                },
            )
            self.logger.info(f"Server {self.host} replied: {response}")

            # If no error was raised, map response to a `ApiResponse` object and return
            return ApiResponse(
                response_code=response.status_code, message=response.text
            )
        except Exception as error:
            self.logger.error(f"{error}")
            raise ApiError(status_code=500, message=f"{error}")
