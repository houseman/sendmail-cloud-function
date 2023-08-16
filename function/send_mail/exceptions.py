class BaseException(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str, *args: object) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"[{self.status_code}] {self.message}"


class ApiException(BaseException):
    pass


class PayloadException(BaseException):
    pass


class ControllerException(BaseException):
    pass
