import dataclasses


@dataclasses.dataclass(repr=True)
class School:
    id: str
    name: str
    name_en: str
    city: str
    address: str
    endpoint: str


@dataclasses.dataclass(repr=True)
class Board:
    id: str
    title: str
    popup: bool
    create_date: str
    group_code: str
    group_name: str
    author: str
    content: str


@dataclasses.dataclass(repr=True)
class Hospital:
    name: str
    state: str
    city: str
    schedule: str
    tell: str
