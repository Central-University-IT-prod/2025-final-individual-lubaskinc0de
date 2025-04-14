from uuid import UUID

from adaptix.conversion import get_converter
from pydantic import BaseModel

from crudik.application.data_model.common import Age
from crudik.domain.entity.client import Client, Gender


class ClientData(BaseModel):
    client_id: UUID
    login: str
    age: Age
    location: str
    gender: Gender


convert_client_to_entity = get_converter(ClientData, Client)
