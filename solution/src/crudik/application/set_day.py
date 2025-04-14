from dataclasses import dataclass

from crudik.application.common.gateway.current_day import DayGateway
from crudik.application.data_model.day import Day
from crudik.application.exceptions.day import CannotSetDayInPastError


@dataclass(slots=True, frozen=True)
class SetDay:
    gateway: DayGateway

    async def execute(self, day: Day) -> Day:
        if day.current_date < await self.gateway.read_current_day():
            raise CannotSetDayInPastError
        await self.gateway.set_current_day(day.current_date)
        return day
