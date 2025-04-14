from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from uuid import UUID

from crudik.application.common.gateway.advertiser import AdvertiserGateway
from crudik.application.common.gateway.campaign import CampaignGateway
from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.common.swear_filter import SwearFilter
from crudik.application.common.uow import UoW
from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily
from crudik.domain.entity.advertiser import Advertiser
from crudik.domain.entity.campaign import Campaign


@dataclass(slots=True)
class MockDayGateway(DayGateway):
    current_day: int = 0

    async def read_current_day(self) -> int:
        return self.current_day

    async def set_current_day(self, day: int) -> None:
        self.current_day = day


class MockCampaignGateway(CampaignGateway):
    def __init__(self) -> None:
        self.campaigns: dict[UUID, Campaign] = {}

    async def get_by_id(self, unique_id: UUID) -> Campaign | None:
        campaign = self.campaigns.get(unique_id)
        return campaign if campaign and not campaign.is_deleted else None

    async def get_by_id_all(self, unique_id: UUID) -> Campaign | None:
        return self.campaigns.get(unique_id)

    async def list(
        self,
        advertiser_id: UUID,
        limit: int | None,
        offset: int | None,
    ) -> Sequence[Campaign]:
        campaigns = [
            campaign
            for campaign in self.campaigns.values()
            if not campaign.is_deleted and campaign.advertiser_id == advertiser_id
        ]
        return campaigns[offset : limit + offset] if limit is not None and offset is not None else campaigns

    async def get_stat(self, unique_id: UUID) -> CampaignStat | None:
        raise NotImplementedError

    async def get_stat_daily(self, unique_id: UUID) -> Sequence[CampaignStatDaily]:
        raise NotImplementedError


class MockAdvertiserGateway(AdvertiserGateway):
    def __init__(self) -> None:
        self.advertisers: dict[UUID, Advertiser] = {}

    async def upsert(self, data: Iterable[Advertiser]) -> Sequence[Advertiser]:
        for advertiser in data:
            self.advertisers[advertiser.advertiser_id] = advertiser
        return list(data)

    async def get_by_id(self, unique_id: UUID) -> Advertiser | None:
        return self.advertisers.get(unique_id)

    async def get_stat(self, advertiser_id: UUID) -> CampaignStat | None:
        raise NotImplementedError

    async def get_stat_daily(self, advertiser_id: UUID) -> Sequence[CampaignStatDaily]:
        raise NotImplementedError


@dataclass(slots=True)
class MockSwearFilter(SwearFilter):
    enabled: bool = False

    async def check_contains_swears(self, text: str) -> bool:
        return self.enabled

    async def set_mode(self, *, enabled: bool) -> None:
        self.enabled = enabled


@dataclass(slots=True)
class MockUoW(UoW):
    campaign_mapper: MockCampaignGateway
    advertiser_mapper: MockAdvertiserGateway

    async def commit(self) -> None: ...

    def add(self, instance: object) -> None:
        if isinstance(instance, Campaign):
            self.campaign_mapper.campaigns[instance.campaign_id] = instance
        elif isinstance(instance, Advertiser):
            self.advertiser_mapper.advertisers[instance.advertiser_id] = instance

    async def delete(self, instance: object) -> None:
        if isinstance(instance, Campaign):
            self.campaign_mapper.campaigns.pop(instance.campaign_id)
        elif isinstance(instance, Advertiser):
            self.advertiser_mapper.advertisers.pop(instance.advertiser_id)
