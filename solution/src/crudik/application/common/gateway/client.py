from abc import abstractmethod
from collections.abc import Iterable, Sequence
from typing import Protocol
from uuid import UUID

from crudik.domain.entity.client import Client


class ClientGateway(Protocol):
    @abstractmethod
    async def upsert(self, data: Iterable[Client]) -> Sequence[Client]: ...

    @abstractmethod
    async def get_by_id(self, unique_id: UUID) -> Client | None: ...
