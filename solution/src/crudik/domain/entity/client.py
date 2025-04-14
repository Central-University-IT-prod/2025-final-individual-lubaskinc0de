from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


@dataclass
class Client:
    client_id: UUID
    login: str
    age: int
    location: str
    gender: Gender
