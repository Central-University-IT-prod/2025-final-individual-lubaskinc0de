from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.domain.entity.advertiser import Advertiser


@dataclass(slots=True, frozen=True)
class ReadAdvertiser:
    gateway: AdvertiserGateway

    async def execute(self, data: UUID) -> Advertiser:
        entry = await self.gateway.get_by_id(data)
        if entry is None:
            raise AdvertiserDoesNotExistsError

        return entry
