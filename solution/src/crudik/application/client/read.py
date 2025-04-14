from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.client import ClientGateway
from crudik.application.exceptions.client import ClientDoesNotExistsError
from crudik.domain.entity.client import Client


@dataclass(slots=True, frozen=True)
class ReadClient:
    gateway: ClientGateway

    async def execute(self, data: UUID) -> Client:
        client = await self.gateway.get_by_id(data)
        if client is None:
            raise ClientDoesNotExistsError

        return client
