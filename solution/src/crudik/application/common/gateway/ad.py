from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from crudik.application.data_model.ad import Ad
from crudik.domain.entity.click import Click
from crudik.domain.entity.client import Client
from crudik.domain.entity.impression import Impression


class AdGateway(Protocol):
    @abstractmethod
    async def get_impression(self, client_id: UUID, ad_id: UUID) -> Impression | None: ...

    @abstractmethod
    async def get_click(self, client_id: UUID, ad_id: UUID) -> Click | None: ...

    @abstractmethod
    async def get_clicks_count(self, ad_id: UUID) -> int: ...

    @abstractmethod
    async def show_ad(self, client: Client, day: int) -> Ad | None: ...
