import logging
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily
from crudik.application.exceptions.advertiser import AdvertiserDoesNotExistsError


@dataclass(slots=True, frozen=True)
class ProduceAdvertiserStat:
    advertiser_gateway: AdvertiserGateway

    async def execute(
        self,
        advertiser_id: UUID,
    ) -> CampaignStat:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        stat = await self.advertiser_gateway.get_stat(advertiser_id)
        if stat is None:
            logging.warning("Cannot produce stat for advertiser %s", advertiser_id)
            raise AdvertiserDoesNotExistsError

        return stat


@dataclass(slots=True, frozen=True)
class ProduceAdvertiserDailyStat:
    advertiser_gateway: AdvertiserGateway

    async def execute(
        self,
        advertiser_id: UUID,
    ) -> Sequence[CampaignStatDaily]:
        advertiser = await self.advertiser_gateway.get_by_id(advertiser_id)
        if advertiser is None:
            raise AdvertiserDoesNotExistsError

        stat = await self.advertiser_gateway.get_stat_daily(advertiser_id)
        return stat
