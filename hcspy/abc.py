from abc import ABCMeta, abstractmethod
from typing import Any, Dict
from json import dumps


class HCSModelABC(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, **response_data: Any) -> None:
        self.response_data = response_data

    @property
    @abstractmethod
    def data(self) -> Dict[str, Any]:
        return self.response_data

    @property
    @abstractmethod
    def wrapped_data(self) -> str:
        return dumps(self.response_data)

    @property
    @abstractmethod
    def is_error(self) -> bool:
        if self.response_data.get("isError"):
            return True
        return False
