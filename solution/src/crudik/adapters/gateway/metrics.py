from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from crudik.adapters.db.models.ad import advertiser_table, campaign_table, click_table, client_table, impression_table
from crudik.application.common.gateway.metrics import MetricsGateway
from crudik.application.data_model.metrics import ServiceMetrics


@dataclass(slots=True, frozen=True)
class MetricsAlchemyGateway(MetricsGateway):
    session: AsyncSession

    async def get_metrics(self) -> ServiceMetrics:
        impressions = (
            select(
                func.count().label("impressions_count"),
                func.coalesce(func.sum(impression_table.c.cost_per_impression), 0.0).label("income_impressions"),
            )
        ).cte()

        clicks = (
            select(
                func.count().label("clicks_count"),
                func.coalesce(func.sum(click_table.c.cost_per_click), 0.0).label("income_clicks"),
            )
        ).cte()

        advertisers = (
            select(
                func.count().label("advertisers_count"),
            ).select_from(advertiser_table)
        ).cte()

        clients = (
            select(
                func.count().label("clients_count"),
            ).select_from(client_table)
        ).cte()

        campaigns = (
            select(
                func.count().label("campaigns_count"),
            ).select_from(campaign_table)
        ).cte()

        conversion = func.coalesce(
            (clicks.c.clicks_count / func.nullif(impressions.c.impressions_count, 0)) * 100,
            0.0,
        )
        income_total = impressions.c.income_impressions + clicks.c.income_clicks

        q = select(
            impressions.c.impressions_count,
            clicks.c.clicks_count,
            advertisers.c.advertisers_count,
            clients.c.clients_count,
            campaigns.c.campaigns_count,
            conversion,
            impressions.c.income_impressions,
            clicks.c.income_clicks,
            income_total,
        )
        result = await self.session.execute(q)
        row = result.one()

        return ServiceMetrics(
            impressions_count=row[0],
            clicks_count=row[1],
            advertisers_count=row[2],
            clients_count=row[3],
            campaigns_count=row[4],
            conversion=row[5],
            income_impressions=row[6],
            income_clicks=row[7],
            income_total=row[8],
        )
