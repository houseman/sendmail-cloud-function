import os
import dotenv

from .send import send_email_task  # noqa: F401


def get_env_file_path() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, ".env")


dotenv.load_dotenv(get_env_file_path())
