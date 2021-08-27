from typing import Any, Dict, Union


class HCSException(Exception):
    pass


class HTTPException(HCSException):
    def __init__(self, code: Any, message: Union[Any, Dict[str, Any]]) -> None:
        self.code = code
        self.message = message

        super().__init__(f"{self.code} {self.message}")


class SchoolNotFound(HCSException):
    pass


class AuthorizeError(HCSException):
    pass


class PasswordLengthError(HCSException):
    pass


class AlreadyAgreed(HCSException):
    pass
