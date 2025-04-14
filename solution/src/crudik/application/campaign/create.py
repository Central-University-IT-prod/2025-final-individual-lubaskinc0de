import logging
from dataclasses import dataclass
from uuid import UUID, uuid4

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.common.uow import UoW
from crudik.application.data_model.campaign import (
    CampaignCreateData,
    CampaignData,
    convert_entity_to_campaign,
)
from crudik.application.exceptions.advertiser import (
    AdvertiserDoesNotExistsError,
)
from crudik.application.exceptions.campaign import (
    CampaignCannotBeInPastError,
    CampaignContainsSwearsError,
    ClickLimitGreaterThanImpressionsLimitError,
)
from crudik.domain.entity.campaign import Campaign


@dataclass(slots=True, frozen=True)
class CreateCampaign:
    uow: UoW
    day_gateway: DayGateway
    campaign_gateway: CampaignGateway
    advertiser_gateway: AdvertiserGateway
    swear_filter: SwearFilter

    async def execute(
        self,
        data: CampaignCreateData,
        advertiser_id: UUID,
    ) -> CampaignData:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        campaign_id = uuid4()
        current_day = await self.day_gateway.read_current_day()

        if data.start_date < current_day:
            raise CampaignCannotBeInPastError

        if data.end_date < current_day:
            raise CampaignCannotBeInPastError

        if data.end_date < data.start_date:
            raise CampaignCannotBeInPastError

        if data.clicks_limit > data.impressions_limit:
            raise ClickLimitGreaterThanImpressionsLimitError

        ad_full_text = data.ad_title + " " + data.ad_text
        if await self.swear_filter.check_contains_swears(ad_full_text):
            raise CampaignContainsSwearsError

        entity = Campaign(
            campaign_id=campaign_id,
            advertiser_id=advertiser_id,
            impressions_limit=data.impressions_limit,
            clicks_limit=data.clicks_limit,
            cost_per_impression=data.cost_per_impression,
            cost_per_click=data.cost_per_click,
            ad_title=data.ad_title,
            ad_text=data.ad_text,
            start_date=data.start_date,
            end_date=data.end_date,
            age_from=data.targeting.age_from if data.targeting is not None else None,
            age_to=data.targeting.age_to if data.targeting is not None else None,
            location=data.targeting.location if data.targeting is not None else None,
            gender=data.targeting.gender if data.targeting is not None else None,
        )

        self.uow.add(entity)
        await self.uow.commit()
        logging.info("Created campaign: %s", campaign_id)
        return convert_entity_to_campaign(entity)
