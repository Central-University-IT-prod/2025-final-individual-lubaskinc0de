from abc import abstractmethod
from typing import Protocol

from crudik.domain.entity.relevance import Relevance


class RelevanceGateway(Protocol):
    @abstractmethod
    async def upsert(self, data: Relevance) -> None: ...
