from dataclasses import dataclass

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.client import ClientGateway
from crudik.application.common.gateway.relevance import RelevanceGateway
from crudik.application.common.uow import UoW
from crudik.application.data_model.relevance import (
    RelevanceData,
    convert_relevance_to_entity,
)
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.client import ClientDoesNotExistsError


@dataclass(slots=True, frozen=True)
class UpsertRelevance:
    gateway: RelevanceGateway
    client_gateway: ClientGateway
    advertiser_gateway: AdvertiserGateway
    comitter: UoW

    async def execute(self, data: RelevanceData) -> None:
        client = await self.client_gateway.get_by_id(data.client_id)

        if client is None:
            raise ClientDoesNotExistsError

        advertiser = await self.advertiser_gateway.get_by_id(data.advertiser_id)

        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        await self.gateway.upsert(convert_relevance_to_entity(data))
        await self.comitter.commit()
