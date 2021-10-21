import logging
from logging import Logger
from typing import Any, Optional

import dotenv


class Config:
    def __init__(self) -> None:
        self._values_ = dotenv.dotenv_values()

    def get_val(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        return self._values_.get(key, default)

    @staticmethod
    def create_logger() -> Logger:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # defaults to WARN

        return logger
