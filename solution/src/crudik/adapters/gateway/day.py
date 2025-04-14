from dataclasses import dataclass

from crudik.adapters.redis import RedisStorage
from crudik.application.common.gateway.current_day import DayGateway

DAY_KEY = "current_day"


@dataclass(slots=True, frozen=True)
class DayRedisGateway(DayGateway):
    client: RedisStorage

    async def set_current_day(self, day: int) -> None:
        await self.client.set(DAY_KEY, str(day))

    async def read_current_day(self) -> int:
        res: str | int | None = await self.client.get(DAY_KEY)
        if res is None:
            await self.set_current_day(0)
            res = 0

        return int(res)
