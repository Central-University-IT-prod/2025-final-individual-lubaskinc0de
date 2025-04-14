from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from crudik.application.ad.click import ClickAd
from crudik.application.ad.show_ad import ShowAd
from crudik.application.data_model.ad import Ad, ClickRequest

router = APIRouter(
    tags=["Ads"],
    route_class=DishkaRoute,
    prefix="/ads",
)


@router.get("/")
async def show_ad(client_id: UUID, command: FromDishka[ShowAd]) -> Ad:
    return await command.execute(client_id)


@router.post("/{ad_id}/click", status_code=204)
async def click_ad(ad_id: UUID, request: ClickRequest, command: FromDishka[ClickAd]) -> None:
    return await command.execute(request, ad_id)
