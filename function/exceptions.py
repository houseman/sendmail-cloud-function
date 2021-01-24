class DuplicateMessageError(Exception):
    pass


class MailServerResponseError(Exception):
    status_code: int
    text: str

    def __init__(self, status_code: int, text: str, *args: object) -> None:
        self.status_code = status_code
        self.text = text
        super().__init__(*args)

    def __str__(self) -> str:
        return self.text
