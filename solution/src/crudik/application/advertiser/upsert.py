from collections.abc import Sequence
from dataclasses import dataclass

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.uow import UoW
from crudik.application.data_model.advertiser import (
    AdvertiserData,
    convert_advertiser_to_entity,
)
from crudik.domain.entity.advertiser import Advertiser


@dataclass(slots=True, frozen=True)
class UpsertAdvertisers:
    gateway: AdvertiserGateway
    comitter: UoW

    async def execute(self, data: list[AdvertiserData]) -> Sequence[Advertiser]:
        if not data:
            return []

        id_map = {each.advertiser_id: convert_advertiser_to_entity(each) for each in data}

        result = await self.gateway.upsert(id_map.values())
        await self.comitter.commit()

        return result
