from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily
from crudik.domain.entity.campaign import Campaign


class CampaignGateway(Protocol):
    @abstractmethod
    async def get_by_id(self, unique_id: UUID) -> Campaign | None:
        """SHOULD return only not deleted entries."""  # noqa: D401

    @abstractmethod
    async def get_by_id_all(self, unique_id: UUID) -> Campaign | None:
        """SHOULD filter on ALL entries."""  # noqa: D401

    @abstractmethod
    async def list(
        self,
        advertiser_id: UUID,
        limit: int | None,
        offset: int | None,
    ) -> Sequence[Campaign]: ...

    @abstractmethod
    async def get_stat(self, unique_id: UUID) -> CampaignStat | None: ...

    @abstractmethod
    async def get_stat_daily(self, unique_id: UUID) -> Sequence[CampaignStatDaily]: ...
