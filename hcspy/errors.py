from typing import Union, Any, Dict


class HCSException(Exception):
    pass


class HTTPException(HCSException):
    def __init__(self, code: Any, message: Union[Any, Dict[str, Any]]):
        self.code = code
        self.message = message

        super().__init__(f"{self.code} {self.message}")
