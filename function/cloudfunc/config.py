import logging
from logging import Logger
from typing import Dict

from dotenv import dotenv_values


class Config:
    _envars: Dict = {}
    MAILGUN_HOST: str = ""
    MAILGUN_DOMAIN: str = ""
    MAILGUN_API_SENDING_KEY: str = ""

    def __init__(self) -> None:
        envars = dotenv_values()

        self._envars = dict(**envars)

    @staticmethod
    def create_logger() -> Logger:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # defaults to WARN

        return logger
