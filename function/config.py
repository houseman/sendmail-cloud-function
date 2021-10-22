from typing import Any, Optional

import dotenv


class Config:
    def __init__(self) -> None:
        self._values_ = dotenv.dotenv_values(".env")

    def get_val(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        return self._values_.get(key, default)
