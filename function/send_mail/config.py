import os


class Config:
    @staticmethod
    def get_env_val(key: str, default: str | None = None) -> str | None:
        return os.environ.get(key, default)
