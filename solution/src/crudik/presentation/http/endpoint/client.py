from collections.abc import Sequence
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from crudik.application.client.read import ReadClient
from crudik.application.client.upsert import UpsertClients
from crudik.application.data_model.client import ClientData
from crudik.domain.entity.client import Client

router = APIRouter(
    tags=["Clients"],
    route_class=DishkaRoute,
    prefix="/clients",
)


@router.post("/bulk", status_code=201)
async def bulk(
    command: FromDishka[UpsertClients],
    data: list[ClientData],
) -> Sequence[Client]:
    return await command.execute(data)


@router.get("/{entry_id}")
async def read(command: FromDishka[ReadClient], entry_id: UUID) -> Client:
    return await command.execute(entry_id)
