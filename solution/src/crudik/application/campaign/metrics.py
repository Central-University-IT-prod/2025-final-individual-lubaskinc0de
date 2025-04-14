import logging
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily
from crudik.application.exceptions.campaign import CampaignDoesNotExistsError


@dataclass(slots=True, frozen=True)
class ProduceCampaignStat:
    campaign_gateway: CampaignGateway

    async def execute(
        self,
        campaign_id: UUID,
    ) -> CampaignStat:
        campaign = await self.campaign_gateway.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        stat = await self.campaign_gateway.get_stat(campaign_id)
        if stat is None:
            logging.warning("Cannot produce stat for %s", campaign_id)
            raise CampaignDoesNotExistsError

        return stat


@dataclass(slots=True, frozen=True)
class ProduceCampaignStatDaily:
    campaign_gateway: CampaignGateway

    async def execute(
        self,
        campaign_id: UUID,
    ) -> Sequence[CampaignStatDaily]:
        campaign = await self.campaign_gateway.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignDoesNotExistsError

        stat = await self.campaign_gateway.get_stat_daily(campaign_id)
        return stat
