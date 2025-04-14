from collections.abc import Sequence
from dataclasses import dataclass

from crudik.application.common.gateway.client import ClientGateway
from crudik.application.common.uow import UoW
from crudik.application.data_model.client import (
    ClientData,
    convert_client_to_entity,
)
from crudik.domain.entity.client import Client


@dataclass(slots=True, frozen=True)
class UpsertClients:
    gateway: ClientGateway
    comitter: UoW

    async def execute(self, data: list[ClientData]) -> Sequence[Client]:
        if not data:
            return []

        id_map = {client.client_id: convert_client_to_entity(client) for client in data}

        result = await self.gateway.upsert(id_map.values())
        await self.comitter.commit()

        return result
