from collections.abc import Sequence
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from crudik.application.advertiser.metrics import ProduceAdvertiserDailyStat, ProduceAdvertiserStat
from crudik.application.campaign.metrics import ProduceCampaignStat, ProduceCampaignStatDaily
from crudik.application.data_model.campaign import CampaignStat, CampaignStatDaily
from crudik.application.data_model.metrics import ServiceMetrics
from crudik.application.metrics import ProduceMetrics

router = APIRouter(
    tags=["Statistics"],
    route_class=DishkaRoute,
    prefix="/stats",
)


@router.get("/campaigns/{campaign_id}")
async def produce_campaign_stat(campaign_id: UUID, command: FromDishka[ProduceCampaignStat]) -> CampaignStat:
    return await command.execute(campaign_id)


@router.get("/campaigns/{campaign_id}/daily")
async def produce_campaign_stat_daily(
    campaign_id: UUID,
    command: FromDishka[ProduceCampaignStatDaily],
) -> Sequence[CampaignStatDaily]:
    return await command.execute(campaign_id)


@router.get("/advertisers/{advertiser_id}/campaigns")
async def produce_advertiser_stat(advertiser_id: UUID, command: FromDishka[ProduceAdvertiserStat]) -> CampaignStat:
    return await command.execute(advertiser_id)


@router.get("/static")
async def produce_service_metrics_static(command: FromDishka[ProduceMetrics]) -> ServiceMetrics:
    return await command.execute()


@router.get("/advertisers/{advertiser_id}/campaigns/daily")
async def produce_advertiser_stat_daily(
    advertiser_id: UUID,
    command: FromDishka[ProduceAdvertiserDailyStat],
) -> Sequence[CampaignStatDaily]:
    return await command.execute(advertiser_id)
