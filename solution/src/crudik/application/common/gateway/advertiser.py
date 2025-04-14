from abc import abstractmethod
from collections.abc import Iterable, Sequence
from typing import Protocol
from uuid import UUID

from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily
from crudik.domain.entity.advertiser import Advertiser


class AdvertiserGateway(Protocol):
    @abstractmethod
    async def upsert(
        self,
        data: Iterable[Advertiser],
    ) -> Sequence[Advertiser]: ...

    @abstractmethod
    async def get_by_id(self, unique_id: UUID) -> Advertiser | None: ...

    @abstractmethod
    async def get_stat(self, advertiser_id: UUID) -> CampaignStat | None: ...

    @abstractmethod
    async def get_stat_daily(self, advertiser_id: UUID) -> Sequence[CampaignStatDaily]: ...
