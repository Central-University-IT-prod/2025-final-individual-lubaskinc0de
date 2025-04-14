from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.data_model.campaign import (
    CampaignData,
    convert_entity_to_campaign,
)
from crudik.application.data_model.common import Pagination
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)


@dataclass(slots=True, frozen=True)
class ListCampaigns:
    campaign_gateway: CampaignGateway
    advertiser_gateway: AdvertiserGateway

    async def execute(
        self,
        advertiser_id: UUID,
        pagination: Pagination,
    ) -> list[CampaignData]:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        limit, offset = None, None
        if pagination.size is not None:
            limit = pagination.size

        if pagination.size is not None and pagination.page is not None:
            offset = pagination.size * pagination.page

        entries = await self.campaign_gateway.list(advertiser_id, limit, offset)
        return [convert_entity_to_campaign(entity) for entity in entries]
