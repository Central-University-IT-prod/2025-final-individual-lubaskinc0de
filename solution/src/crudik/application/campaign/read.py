from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.data_model.campaign import (
    CampaignData,
    convert_entity_to_campaign,
)
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.campaign import CampaignDoesNotExistsError
from crudik.domain.error.base import AccessDeniedError


@dataclass(slots=True, frozen=True)
class ReadCampaign:
    campaign_gateway: CampaignGateway
    advertiser_gateway: AdvertiserGateway

    async def execute(
        self,
        campaign_id: UUID,
        advertiser_id: UUID,
    ) -> CampaignData:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        campaign = await self.campaign_gateway.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        if campaign.advertiser_id != advertiser_id:
            raise AccessDeniedError

        return convert_entity_to_campaign(campaign)
