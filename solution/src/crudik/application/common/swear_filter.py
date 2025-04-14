from abc import abstractmethod
from typing import Protocol


class SwearFilter(Protocol):
    @abstractmethod
    async def check_contains_swears(self, text: str) -> bool: ...

    @abstractmethod
    async def set_mode(self, *, enabled: bool) -> None: ...
