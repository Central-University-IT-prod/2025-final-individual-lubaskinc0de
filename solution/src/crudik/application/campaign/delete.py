import logging
from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.uow import UoW
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.campaign import CampaignDoesNotExistsError
from crudik.domain.error.base import AccessDeniedError


@dataclass(slots=True, frozen=True)
class DeleteCampaign:
    uow: UoW
    campaign_gateway: CampaignGateway
    advertiser_gateway: AdvertiserGateway

    async def execute(self, campaign_id: UUID, advertiser_id: UUID) -> None:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        campaign = await self.campaign_gateway.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        if campaign.advertiser_id != advertiser_id:
            raise AccessDeniedError

        campaign.is_deleted = True
        await self.uow.commit()
        logging.info("Deleted %s", campaign.campaign_id)
