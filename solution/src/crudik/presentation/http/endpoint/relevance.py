from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from crudik.application.data_model.relevance import RelevanceData
from crudik.application.relevance.upsert import UpsertRelevance

router = APIRouter(
    tags=["ML Scores"],
    route_class=DishkaRoute,
    prefix="/ml-scores",
)


@router.post("/")
async def upsert(
    command: FromDishka[UpsertRelevance],
    data: RelevanceData,
) -> None:
    return await command.execute(data)
