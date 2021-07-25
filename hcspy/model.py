import dataclasses


@dataclasses.dataclass(repr=True)
class School:
    id: str
    name: str
    name_en: str
    city: str
    address: str
    endpoint: str
