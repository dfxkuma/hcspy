
from dataclasses import dataclass


@dataclass(repr=True)
class School:
    id: str
    name: str
    name_en: str
    city: str
    address: str
    endpoint: str


@dataclass(repr=True)
class Board:
    id: str
    title: str
    popup: bool
    create_date: str
    group_code: str
    group_name: str
    author: str
    content: str


@dataclass(repr=True)
class Hospital:
    name: str
    state: str
    city: str
    schedule_weekday: str
    schedule_saturday: str
    schedule_sunday: str
    tell: str
    map_url: str
