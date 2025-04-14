from abc import abstractmethod
from typing import Protocol


class UoW(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    def add(self, instance: object) -> None: ...

    @abstractmethod
    async def delete(self, instance: object) -> None: ...
