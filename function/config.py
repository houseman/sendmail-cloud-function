import os
from typing import Optional


def get_env_val(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)
