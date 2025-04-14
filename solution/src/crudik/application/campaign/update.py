from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.common.uow import UoW
from crudik.application.data_model.campaign import (
    CampaignData,
    CampaignUpdateData,
    convert_entity_to_campaign,
)
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.campaign import (
    CampaignCannotBeInPastError,
    CampaignContainsSwearsError,
    CampaignDoesNotExistsError,
    CannotChangeCampaignAfterStartError,
)
from crudik.domain.error.base import AccessDeniedError


@dataclass(slots=True, frozen=True)
class UpdateCampaign:
    campaign_gateway: CampaignGateway
    advertiser_gateway: AdvertiserGateway
    uow: UoW
    day_gateway: DayGateway
    swear_filter: SwearFilter

    async def execute(
        self,
        campaign_id: UUID,
        advertiser_id: UUID,
        data: CampaignUpdateData,
    ) -> CampaignData:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        campaign = await self.campaign_gateway.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        if campaign.advertiser_id != advertiser_id:
            raise AccessDeniedError

        current_day = await self.day_gateway.read_current_day()

        if (
            (
                data.impressions_limit,
                data.clicks_limit,
                data.start_date,
                data.end_date,
            )
            != (
                campaign.impressions_limit,
                campaign.clicks_limit,
                campaign.start_date,
                campaign.end_date,
            )
        ) and campaign.is_started(current_day):
            raise CannotChangeCampaignAfterStartError

        if data.start_date < current_day:
            raise CampaignCannotBeInPastError

        if data.end_date < current_day:
            raise CampaignCannotBeInPastError

        if data.end_date < data.start_date:
            raise CampaignCannotBeInPastError

        ad_full_text = data.ad_title + " " + data.ad_text
        if await self.swear_filter.check_contains_swears(ad_full_text):
            raise CampaignContainsSwearsError

        campaign.impressions_limit = data.impressions_limit
        campaign.clicks_limit = data.clicks_limit
        campaign.start_date = data.start_date
        campaign.end_date = data.end_date

        campaign.cost_per_impression = data.cost_per_impression
        campaign.cost_per_click = data.cost_per_click
        campaign.ad_title = data.ad_title
        campaign.ad_text = data.ad_text

        campaign.age_from = data.targeting.age_from if data.targeting else None
        campaign.age_to = data.targeting.age_to if data.targeting else None
        campaign.location = data.targeting.location if data.targeting else None
        campaign.gender = data.targeting.gender if data.targeting else None

        await self.uow.commit()
        return convert_entity_to_campaign(campaign)
