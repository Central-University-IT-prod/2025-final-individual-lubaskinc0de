from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from crudik.application.data_model.day import Day
from crudik.application.set_day import SetDay

router = APIRouter(
    tags=["Time"],
    route_class=DishkaRoute,
    prefix="/time",
)


@router.post("/advance")
async def advance(command: FromDishka[SetDay], data: Day) -> Day:
    return await command.execute(data)
