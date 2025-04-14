from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


class DayGateway(Protocol):
    @abstractmethod
    async def read_current_day(self) -> int: ...

    @abstractmethod
    async def set_current_day(self, day: int) -> None: ...


@dataclass(slots=True)
class MockDayGateway(DayGateway):
    current_day: int = 0

    async def read_current_day(self) -> int:
        return self.current_day

    async def set_current_day(self, day: int) -> None:
        self.current_day = day
