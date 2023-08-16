import os


def get_env_str(key: str, default: str = "") -> str:
    val = os.environ.get(key)
    if val is None:
        return default

    return str(val)


def get_env_int(key: str, default: int = 0) -> int:
    val = os.environ.get(key)
    if val is None:
        return default

    return int(val)
